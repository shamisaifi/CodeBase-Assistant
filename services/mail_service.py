import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import settings


def send_email(to: str, subject: str, html_body: str, text_body: str | None = None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to

    if text_body:
        msg.attach(MIMEText(text_body, "plain"))

    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.sendmail(settings.SMTP_FROM, to, msg.as_string())


# ─────────────────────────────────────────────
# SHARED BASE TEMPLATE
# ─────────────────────────────────────────────
def _base_template(content: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Codebase Assistant</title>
</head>
<body style="margin:0;padding:0;background:#0f1117;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background:#0f1117;min-height:100vh;padding:40px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;width:100%;background:#161b27;border-radius:16px;
                      border:1px solid #1e2d40;overflow:hidden;">

          <!-- Header bar -->
          <tr>
            <td style="background:linear-gradient(135deg,#1a2942 0%,#0d1f35 100%);
                       padding:32px 40px;border-bottom:1px solid #1e2d40;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <!-- Logo mark -->
                    <span style="display:inline-block;width:36px;height:36px;
                                 background:linear-gradient(135deg,#3b82f6,#6366f1);
                                 border-radius:8px;text-align:center;line-height:36px;
                                 font-size:18px;vertical-align:middle;margin-right:10px;">⬡</span>
                    <span style="font-size:18px;font-weight:700;color:#e2e8f0;
                                 vertical-align:middle;letter-spacing:-0.3px;">
                      Codebase<span style="color:#3b82f6;">.</span>ai
                    </span>
                  </td>
                  <td align="right">
                    <span style="font-size:11px;color:#4a6380;letter-spacing:1.5px;
                                 text-transform:uppercase;font-weight:600;">
                      Automated
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Body content injected here -->
          {content}

          <!-- Footer -->
          <tr>
            <td style="padding:24px 40px;border-top:1px solid #1e2d40;
                       background:#0f1117;">
              <p style="margin:0 0 6px;font-size:12px;color:#3a4a5c;text-align:center;">
                This is an automated message from Codebase Assistant.
              </p>
              <p style="margin:0;font-size:12px;color:#3a4a5c;text-align:center;">
                If you did not request this, you can safely ignore this email.
              </p>
              <p style="margin:16px 0 0;font-size:11px;color:#2a3540;text-align:center;
                        letter-spacing:0.5px;">
                © 2025 Codebase Assistant · All rights reserved
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>

</body>
</html>
"""


# ─────────────────────────────────────────────
# WELCOME EMAIL — sent on register
# ─────────────────────────────────────────────
def send_welcome_email(to: str, username: str):
    content = f"""
          <!-- Hero -->
          <tr>
            <td style="padding:48px 40px 32px;">
              <p style="margin:0 0 8px;font-size:12px;color:#3b82f6;letter-spacing:2px;
                         text-transform:uppercase;font-weight:600;">
                Account Created
              </p>
              <h1 style="margin:0 0 16px;font-size:28px;font-weight:700;
                          color:#e2e8f0;line-height:1.2;letter-spacing:-0.5px;">
                Welcome aboard,<br/>{username} 👋
              </h1>
              <p style="margin:0;font-size:15px;color:#7a8fa6;line-height:1.6;">
                Your Codebase Assistant account is ready. Upload your code, ask questions,
                and let the AI do the heavy lifting.
              </p>
            </td>
          </tr>

          <!-- Divider -->
          <tr>
            <td style="padding:0 40px;">
              <div style="height:1px;background:linear-gradient(90deg,transparent,#1e2d40,transparent);"></div>
            </td>
          </tr>

          <!-- Feature pills -->
          <tr>
            <td style="padding:32px 40px;">
              <p style="margin:0 0 20px;font-size:13px;color:#4a6380;
                         text-transform:uppercase;letter-spacing:1.5px;font-weight:600;">
                What you can do
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="padding:0 8px 12px 0;" width="50%">
                    <div style="background:#1a2435;border:1px solid #1e2d40;border-radius:10px;
                                padding:16px;border-left:3px solid #3b82f6;">
                      <div style="font-size:20px;margin-bottom:8px;">📁</div>
                      <div style="font-size:13px;font-weight:600;color:#cbd5e1;
                                  margin-bottom:4px;">Upload Code</div>
                      <div style="font-size:12px;color:#4a6380;line-height:1.5;">
                        Any language, any file type
                      </div>
                    </div>
                  </td>
                  <td style="padding:0 0 12px 8px;" width="50%">
                    <div style="background:#1a2435;border:1px solid #1e2d40;border-radius:10px;
                                padding:16px;border-left:3px solid #6366f1;">
                      <div style="font-size:20px;margin-bottom:8px;">🤖</div>
                      <div style="font-size:13px;font-weight:600;color:#cbd5e1;
                                  margin-bottom:4px;">Ask Anything</div>
                      <div style="font-size:12px;color:#4a6380;line-height:1.5;">
                        Powered by Groq LLM
                      </div>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="padding:0 8px 0 0;" width="50%">
                    <div style="background:#1a2435;border:1px solid #1e2d40;border-radius:10px;
                                padding:16px;border-left:3px solid #10b981;">
                      <div style="font-size:20px;margin-bottom:8px;">⚡</div>
                      <div style="font-size:13px;font-weight:600;color:#cbd5e1;
                                  margin-bottom:4px;">Instant Answers</div>
                      <div style="font-size:12px;color:#4a6380;line-height:1.5;">
                        Vector search + RAG
                      </div>
                    </div>
                  </td>
                  <td style="padding:0 0 0 8px;" width="50%">
                    <div style="background:#1a2435;border:1px solid #1e2d40;border-radius:10px;
                                padding:16px;border-left:3px solid #f59e0b;">
                      <div style="font-size:20px;margin-bottom:8px;">💾</div>
                      <div style="font-size:13px;font-weight:600;color:#cbd5e1;
                                  margin-bottom:4px;">Chat History</div>
                      <div style="font-size:12px;color:#4a6380;line-height:1.5;">
                        All sessions saved
                      </div>
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding:0 40px 48px;" align="center">
              <a href="http://localhost:8000"
                 style="display:inline-block;background:linear-gradient(135deg,#3b82f6,#6366f1);
                        color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;
                        padding:14px 36px;border-radius:8px;letter-spacing:0.3px;">
                Open Codebase Assistant →
              </a>
            </td>
          </tr>
    """
    html = _base_template(content)
    send_email(to, "Welcome to Codebase Assistant", html)


# ─────────────────────────────────────────────
# LOGIN ALERT — sent on each login
# ─────────────────────────────────────────────
def send_login_alert_email(to: str, username: str, login_time: str, ip: str = "Unknown"):
    content = f"""
          <!-- Alert header -->
          <tr>
            <td style="padding:48px 40px 24px;">
              <p style="margin:0 0 8px;font-size:12px;color:#10b981;letter-spacing:2px;
                         text-transform:uppercase;font-weight:600;">
                Security Alert
              </p>
              <h1 style="margin:0 0 12px;font-size:26px;font-weight:700;
                          color:#e2e8f0;line-height:1.2;letter-spacing:-0.5px;">
                New sign-in detected
              </h1>
              <p style="margin:0;font-size:15px;color:#7a8fa6;line-height:1.6;">
                Hi <strong style="color:#cbd5e1;">{username}</strong>, 
                your account was just accessed.
              </p>
            </td>
          </tr>

          <!-- Info card -->
          <tr>
            <td style="padding:0 40px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#1a2435;border:1px solid #1e2d40;
                            border-radius:12px;overflow:hidden;">
                <tr>
                  <td style="padding:20px 24px;border-bottom:1px solid #1e2d40;">
                    <table width="100%">
                      <tr>
                        <td style="font-size:12px;color:#4a6380;
                                   text-transform:uppercase;letter-spacing:1px;
                                   font-weight:600;">Time</td>
                        <td align="right" style="font-size:13px;color:#cbd5e1;
                                                  font-weight:500;">{login_time}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:20px 24px;">
                    <table width="100%">
                      <tr>
                        <td style="font-size:12px;color:#4a6380;
                                   text-transform:uppercase;letter-spacing:1px;
                                   font-weight:600;">IP Address</td>
                        <td align="right" style="font-size:13px;color:#cbd5e1;
                                                  font-weight:500;font-family:monospace;">
                          {ip}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Not you? -->
          <tr>
            <td style="padding:0 40px 48px;">
              <div style="background:#1f1a2e;border:1px solid #2d1f4a;border-radius:10px;
                          padding:20px 24px;">
                <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#a78bfa;">
                  ⚠️  Wasn't you?
                </p>
                <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;">
                  If you did not sign in, reset your password immediately to secure your account.
                </p>
              </div>
            </td>
          </tr>
    """
    html = _base_template(content)
    send_email(to, "New sign-in to your Codebase Assistant account", html)


# ─────────────────────────────────────────────
# OTP EMAIL — sent on password reset request
# ─────────────────────────────────────────────
def send_otp_email(to: str, otp: str, username: str):
    # split OTP digits for individual box rendering
    digits = list(otp.zfill(6))
    digit_boxes = "".join([
        f"""<td style="width:48px;height:56px;background:#1a2435;border:1px solid #1e2d40;
                       border-radius:8px;text-align:center;vertical-align:middle;
                       font-size:26px;font-weight:700;color:#3b82f6;
                       font-family:'Courier New',monospace;letter-spacing:0;
                       padding:0 4px;">
              {d}
            </td>
            <td style="width:6px;"></td>"""
        for d in digits
    ])

    content = f"""
          <!-- Header -->
          <tr>
            <td style="padding:48px 40px 32px;">
              <p style="margin:0 0 8px;font-size:12px;color:#f59e0b;letter-spacing:2px;
                         text-transform:uppercase;font-weight:600;">
                Password Reset
              </p>
              <h1 style="margin:0 0 12px;font-size:26px;font-weight:700;
                          color:#e2e8f0;line-height:1.2;letter-spacing:-0.5px;">
                Your verification code
              </h1>
              <p style="margin:0;font-size:15px;color:#7a8fa6;line-height:1.6;">
                Hi <strong style="color:#cbd5e1;">{username}</strong>, 
                use the code below to reset your password.
              </p>
            </td>
          </tr>

          <!-- OTP boxes -->
          <tr>
            <td style="padding:0 40px 32px;" align="center">
              <div style="background:#0f1117;border:1px solid #1e2d40;border-radius:12px;
                          padding:32px 24px;display:inline-block;">
                <table cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    {digit_boxes}
                  </tr>
                </table>
              </div>
            </td>
          </tr>

          <!-- Expiry warning -->
          <tr>
            <td style="padding:0 40px 32px;" align="center">
              <div style="display:inline-block;background:#1f1a12;
                          border:1px solid #3a2e0a;border-radius:8px;
                          padding:12px 24px;">
                <span style="font-size:13px;color:#f59e0b;font-weight:500;">
                  ⏱ Expires in 10 minutes
                </span>
              </div>
            </td>
          </tr>

          <!-- Security note -->
          <tr>
            <td style="padding:0 40px 48px;">
              <div style="background:#1a1f2e;border:1px solid #1e2d40;
                          border-radius:10px;padding:20px 24px;">
                <p style="margin:0;font-size:13px;color:#4a6380;line-height:1.6;">
                  🔒 Never share this code with anyone. 
                  Codebase Assistant will never ask for your OTP over chat or phone.
                </p>
              </div>
            </td>
          </tr>
    """
    html = _base_template(content)
    send_email(to, "Your password reset code", html)


def send_password_reset_success_email(to: str, ip: str):
    from datetime import datetime, timezone
    time = datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p UTC")
    content = f"""
          <tr>
            <td style="padding:48px 40px 32px;">
              <p style="margin:0 0 8px;font-size:12px;color:#10b981;letter-spacing:2px;
                         text-transform:uppercase;font-weight:600;">Security Notice</p>
              <h1 style="margin:0 0 12px;font-size:26px;font-weight:700;
                          color:#e2e8f0;letter-spacing:-0.5px;">
                Password changed ✓
              </h1>
              <p style="margin:0;font-size:15px;color:#7a8fa6;line-height:1.6;">
                Your Codebase Assistant password was successfully reset.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:0 40px 32px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#1a2435;border:1px solid #1e2d40;border-radius:12px;">
                <tr>
                  <td style="padding:20px 24px;border-bottom:1px solid #1e2d40;">
                    <table width="100%"><tr>
                      <td style="font-size:12px;color:#4a6380;text-transform:uppercase;
                                 letter-spacing:1px;font-weight:600;">Time</td>
                      <td align="right" style="font-size:13px;color:#cbd5e1;">{time}</td>
                    </tr></table>
                  </td>
                </tr>
                <tr>
                  <td style="padding:20px 24px;">
                    <table width="100%"><tr>
                      <td style="font-size:12px;color:#4a6380;text-transform:uppercase;
                                 letter-spacing:1px;font-weight:600;">IP Address</td>
                      <td align="right" style="font-size:13px;color:#cbd5e1;
                                               font-family:monospace;">{ip}</td>
                    </tr></table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:0 40px 48px;">
              <div style="background:#1f1a2e;border:1px solid #2d1f4a;
                          border-radius:10px;padding:20px 24px;">
                <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#a78bfa;">
                  ⚠️ Wasn't you?
                </p>
                <p style="margin:0;font-size:13px;color:#6b7280;line-height:1.6;">
                  If you did not reset your password, contact support immediately
                  and secure your account.
                </p>
              </div>
            </td>
          </tr>
    """
    html = _base_template(content)
    send_email(to, "Your password has been reset", html)
