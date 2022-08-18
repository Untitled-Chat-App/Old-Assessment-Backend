""" (module)
Variables which contain HTML that will be put in emails
"""

__all__ = ["reset_password_email", "welcome_email_html"]

reset_password_email = """
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">
<meta http-equiv="x-ua-compatible" content="ie=edge">
<title>Password Reset</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style type="text/css">
@media screen {
    @font-face {
    font-family: 'Source Sans Pro';
    font-style: normal;
    font-weight: 400;
    src: local('Source Sans Pro Regular'), local('SourceSansPro-Regular'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/ODelI1aHBYDBqgeIAH2zlBM0YzuT7MdOe03otPbuUS0.woff) format('woff');
    }

    @font-face {
    font-family: 'Source Sans Pro';
    font-style: normal;
    font-weight: 700;
    src: local('Source Sans Pro Bold'), local('SourceSansPro-Bold'), url(https://fonts.gstatic.com/s/sourcesanspro/v10/toadOcfmlt9b38dHJxOBGFkQc6VGVFSmCnC_l7QZG60.woff) format('woff');
    }
}
body,
table,
td,
a {
    -ms-text-size-adjust: 100%; /* 1 */
    -webkit-text-size-adjust: 100%; /* 2 */
}

table,
td {
    mso-table-rspace: 0pt;
    mso-table-lspace: 0pt;
}


img {
    -ms-interpolation-mode: bicubic;
}

a[x-apple-data-detectors] {
    font-family: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    line-height: inherit !important;
    color: inherit !important;
    text-decoration: none !important;
}


div[style*="margin: 16px 0;"] {
    margin: 0 !important;
}

body {
    width: 100% !important;
    height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}


table {
    border-collapse: collapse !important;
}

a {
    color: #1a82e2;
}

img {
    height: auto;
    line-height: 100%;
    text-decoration: none;
    border: 0;
    outline: none;
}
</style>

</head>
<body style="background-color: #e9ecef;">
<table border="0" cellpadding="0" cellspacing="0" width="100%">
    <tr>
    <td align="center" bgcolor="#e9ecef">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
        <tr>
            <td align="center" valign="top" style="padding: 36px 24px;">
            <a href="https://chatapi.fusionsid.xyz" target="_blank" style="display: inline-block;">
                <img src="https://raw.githubusercontent.com/Untitled-Chat-App/Frontend/main/src/assets/images/logos/nobg_logo_text.png" alt="Logo" border="0" width="420" style="display: block;">
            </a>
            </td>
        </tr>
        </table>
    </td>
    </tr>
    <tr>
    <td align="center" bgcolor="#e9ecef">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
        <tr>
            <td align="left" bgcolor="#ffffff" style="padding: 36px 24px 0; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; border-top: 3px solid #d4dadf;">
            <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -1px; line-height: 48px;">Reset Your Password</h1>
            </td>
        </tr>
        </table>
    </td>
    </tr>
    <tr>
    <td align="center" bgcolor="#e9ecef">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
        <tr>
            <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
            <p style="margin: 0;">Tap the button below to reset your account password. If you didn't request a new password, you can safely delete this email.</p>
            </td>
        </tr>
        <tr>
            <td align="left" bgcolor="#ffffff">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                <td align="center" bgcolor="#ffffff" style="padding: 12px;">
                    <table border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="center" bgcolor="#1a82e2" style="border-radius: 6px;">
                        <a href="https://chatapi.fusionsid.xyz/forgot-password?reset_token=encoded_jwt" target="_blank" style="display: inline-block; padding: 16px 36px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 6px;">Reset Password</a>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
            </td>
        </tr>
        <tr>
            <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px;">
            <p style="margin: 0;">If that doesn't work, skill issue. Also if you wanna read the API docs here is your reset token (valid for 15 minutes):</p>
            <p style="margin: 0;">encoded_jwt</p>
            </td>
        </tr>
        <tr>
            <td align="left" bgcolor="#ffffff" style="padding: 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 24px; border-bottom: 3px solid #d4dadf">
            <p style="margin: 0;">Thanks,<br>FusionSid</p>
            </td>
        </tr>
        </table>
    </td>
    </tr>
    <tr>
    <td align="center" bgcolor="#e9ecef" style="padding: 24px;">
        <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
        <tr>
            <td align="center" bgcolor="#e9ecef" style="padding: 12px 24px; font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; font-size: 14px; line-height: 20px; color: #666;">
            <p style="margin: 0;">You received this email because we received a request to reset the password for your account. If you didn't request to reset your password you can safely delete/ignore this email.</p>
            </td>
        </tr>
        </table>
    </td>
    </tr>
</table>
</body>
</html>
"""

welcome_email_html = """
    <!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
    <meta content="width=device-width, initial-scale=1" name="viewport">
    <style type="text/css">
        @import url(https://fonts.googleapis.com/css?family=Nunito);

        img {
            max-width: 600px;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }

        html {
            margin: 0;
            padding: 0;
        }

        a {
            text-decoration: none;
            border: 0;
            outline: none;
            color: #bbbbbb;
        }

        a img {
            border: none;
        }

        td,
        h1,
        h2,
        h3 {
            font-family: Helvetica, Arial, sans-serif;
            font-weight: 400;
        }

        td {
            text-align: center;
        }

        body {
            -webkit-font-smoothing: antialiased;
            -webkit-text-size-adjust: none;
            width: 100%;
            height: 100%;
            color: #666;
            background: #fff;
            font-size: 16px;
            height: 100vh;
            width: 100%;
            padding: 0px;
            margin: 0px;
        }

        table {
            border-collapse: collapse !important;
        }

        .headline {
            color: #444;
            font-size: 36px;
        }

        .force-full-width {
            width: 100% !important;
        }
    </style>
    <style media="screen" type="text/css">
        @media screen {

            td,
            h1,
            h2,
            h3 {
                font-family: 'Nunito', 'Helvetica Neue', 'Arial', 'sans-serif' !important;
            }
        }
    </style>
    <style media="only screen and (max-width: 480px)" type="text/css">
        /* Mobile styles */
        @media only screen and (max-width: 480px) {

            table[class="w320"] {
                width: 320px !important;
            }
        }
    </style>
    <style type="text/css"></style>

</head>

<body bgcolor="#fff" class="body"
    style="padding:20px; margin:0; display:block; background:#ffffff; -webkit-text-size-adjust:none">
    <table align="center" cellpadding="0" cellspacing="0" height="100%" width="100%">
        <tbody>
            <tr>
                <td align="center" bgcolor="#fff" class="" valign="top" width="100%">
                    <table cellpadding="0" cellspacing="0" class="w320" style="margin: 0 auto;" width="600">
                        <tbody>
                            <tr>
                                <td align="center" class="" valign="top">
                                    <table cellpadding="0" cellspacing="0" style="margin: 0 auto;" width="100%">
                                    </table>
                                    <table bgcolor="#fff" cellpadding="0" cellspacing="0" class=""
                                        style="margin: 0 auto; width: 100%; margin-top: 100px;">
                                        <tbody style="margin-top: 15px;">
                                            <tr class="">
                                                <td class="">
                                                    <img alt="robot picture" class=""
                                                        src="https://raw.githubusercontent.com/Untitled-Chat-App/Frontend/main/src/assets/images/logos/nobg_logo_text.png"
                                                        width="420"> <br><br><br>
                                                </td>
                                            </tr>
                                            <tr class="">
                                                <td class="headline">Welcome to Untitled-Chat!</td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <table cellpadding="0" cellspacing="0" class=""
                                                        style="margin: 0 auto;" width="75%">
                                                        <tbody class="">
                                                            <tr class="">
                                                                <td class="" style="color:#444; font-weight: 400;">
                                                                    <br>
                                                                    Hello {username}!<br>
                                                                    Thank you so much for creating an account, we are so happy you're here.<br><br>
                                                                    <strong>Useful Links:</strong><br>
                                                                    <h3>
                                                                        <a href="https://chatapi.fusionsid.xyz/">API Url</a><br>
                                                                        <a href="https://chatapi.fusionsid.xyz/documentation">API Docs</a><br>
                                                                        <a href="https://github.com/Untitled-Chat-App">Github / Source Code</a><br>
                                                                    </h3>
                                                                    <br><br>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td class="">
                                                    <div class="">
                                                        <a style="background-color:#674299;border-radius:4px;color:#fff;display:inline-block;font-family:Helvetica, Arial, sans-serif;font-size:18px;font-weight:normal;line-height:50px;text-align:center;text-decoration:none;width:350px;-webkit-text-size-adjust:none;"
                                                            href="https://chatapi.fusionsid.xyz/web?room_id=690420690&username={username}">Join "We be copy pastin" Room :)</a>
                                                    </div>
                                                    <br>
                                                </td>
                                            </tr>
                                        </tbody>

                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </tbody>
    </table>
</body>

</html>
"""