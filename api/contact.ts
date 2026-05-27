import { Resend } from 'resend';

export const runtime = 'nodejs';

const MAX_NAME = 200;
const MAX_EMAIL = 200;
const MAX_PHONE = 50;
const MAX_MESSAGE = 5000;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

type Body = {
  name?: string;
  email?: string;
  phone?: string;
  message?: string;
  company?: string;
};

export async function POST(request: Request): Promise<Response> {
  let body: Body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'Invalid request.' }, 400);
  }

  const name = (body.name ?? '').trim();
  const email = (body.email ?? '').trim();
  const phone = (body.phone ?? '').trim();
  const message = (body.message ?? '').trim();
  const honeypot = (body.company ?? '').trim();

  // Bots fill every field; real visitors leave this empty.
  // Respond 200 so bots can't tell they were filtered.
  if (honeypot.length > 0) {
    return json({ ok: true });
  }

  if (!name || name.length > MAX_NAME) {
    return json({ error: 'Please include your name.' }, 400);
  }
  if (!email || email.length > MAX_EMAIL || !EMAIL_RE.test(email)) {
    return json({ error: 'Please include a valid email.' }, 400);
  }
  if (phone.length > MAX_PHONE) {
    return json({ error: 'Phone number looks too long.' }, 400);
  }
  if (!message || message.length > MAX_MESSAGE) {
    return json({ error: 'Please include a short message.' }, 400);
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error('[/api/contact] RESEND_API_KEY is not set');
    return json(
      { error: 'Contact form is temporarily unavailable. Email mark@markgores.com directly.' },
      503,
    );
  }

  // `from:` must use a Resend-verified domain. Only priorlake.realestate is
  // verified, so we send from there and rely on the subject + replyTo (visitor's
  // email) to make replies work naturally.
  const fromAddress =
    process.env.CONTACT_FROM_EMAIL ?? 'markgores.com <noreply@priorlake.realestate>';
  const toAddress = process.env.CONTACT_TO_EMAIL ?? 'mark@markgores.com';
  const bccAddress = process.env.CONTACT_BCC_EMAIL;

  const text = [
    'New contact form submission from markgores.com',
    '',
    `Name:    ${name}`,
    `Email:   ${email}`,
    `Phone:   ${phone || '(not provided)'}`,
    '',
    'Message:',
    message,
    '',
    `Submitted ${new Date().toISOString()}`,
  ].join('\n');

  const subject = `New contact from markgores.com: ${name}`;

  try {
    const resend = new Resend(apiKey);
    const { error } = await resend.emails.send({
      from: fromAddress,
      to: [toAddress],
      bcc: bccAddress ? [bccAddress] : undefined,
      replyTo: email,
      subject,
      text,
    });

    if (error) {
      console.error('[/api/contact] Resend error:', error);
      return json(
        { error: "Couldn't send right now. Try again, or email mark@markgores.com directly." },
        502,
      );
    }

    return json({ ok: true });
  } catch (err) {
    console.error('[/api/contact] Unexpected error:', err);
    return json(
      { error: "Couldn't send right now. Try again, or email mark@markgores.com directly." },
      500,
    );
  }
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
