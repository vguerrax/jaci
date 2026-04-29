import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("jaci.email")

# Configuração do FastMail
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_user,
    MAIL_PASSWORD=settings.smtp_password,
    MAIL_FROM=settings.smtp_from,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smtp_host,
    MAIL_STARTTLS=settings.smtp_tls,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fastmail = FastMail(mail_config)


def _build_magic_link(token: str, group_id : int | None = None) -> str:
    """Monta a URL completa do magic link."""
    return f"{settings.app_url}/auth/verify?token={token}{f'&group_id={group_id}' if group_id else ''}"


async def send_magic_link(email: str, token: str, group_id: int | None = None, group_name: str | None = None, invited_by: str | None = None) -> bool:
    """
    Envia e-mail com magic link.
    Se SMTP não configurado, faz log do link (modo dev).
    Retorna True se o e-mail foi enviado (ou logado com sucesso).
    """
    magic_link = _build_magic_link(token, group_id)
    
    is_invite = group_id and group_name and invited_by
    
    if is_invite:
        subject = f"{invited_by} convidou você para o grupo {group_name} — Jaci 🌙"
        html_body = _build_invite_email(group_name, invited_by, magic_link)
    else:
        subject = "Acesse o Jaci 🌙"
        html_body = _build_login_email(magic_link)

    # Modo mock: SMTP não configurado
    if settings.smtp_mock:
        logger.info("=" * 60)
        logger.info(f"MAGIC LINK para {email}:")
        logger.info(f"  {magic_link}")
        logger.info("=" * 60)
        return True

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=html_body,
        subtype="html",
    )
 
    try:
        await fastmail.send_message(message)
        if is_invite:
            logger.info(f"Convite enviado para {email} (grupo: {group_name})")
        else:
            logger.info(f"Magic link enviado para {email}")
        return True
    except Exception as e:
        logger.error(f"Falha ao enviar e-mail para {email}: {e}")
        return False
    
    
def _build_login_email(magic_link: str) -> str:
    """Template HTML para e-mail de login."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Inter, -apple-system, sans-serif; background: #F5F0E8; padding: 24px; margin: 0;">
        <div style="max-width: 480px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; padding: 40px 32px; text-align: center; border: 1px solid #D9C4B0;">
            <!-- Logo -->
            <div style="margin-bottom: 24px;">
                <span style="font-size: 40px;">🌙</span>
            </div>
            
            <h1 style="color: #2A4B4A; font-size: 24px; font-weight: 600; margin: 0 0 8px 0;">Jaci</h1>
            <p style="color: #D9B382; font-size: 14px; margin: 0 0 24px 0;">Mãe dos Frutos — organize sua colheita</p>
            
            <p style="color: #2A4B4A; font-size: 16px; line-height: 1.6; margin: 0 0 24px 0;">
                Clique no botão abaixo para acessar suas listas de compras.
            </p>
            
            <a href="{magic_link}"
               style="display: inline-block; background: #2A4B4A; color: #F5F0E8; padding: 14px 40px; border-radius: 32px; text-decoration: none; font-weight: 500; font-size: 16px; margin: 8px 0;">
                Entrar no Jaci ✦
            </a>
            
            <p style="color: #8BA7B8; font-size: 12px; margin: 24px 0 0 0; line-height: 1.5;">
                Este link expira em {settings.magic_link_expire_minutes} minutos.<br>
                Se você não solicitou este acesso, ignore este e-mail.
            </p>
            
            <hr style="border: none; border-top: 1px solid #D9C4B0; margin: 24px 0;">
            
            <p style="color: #D9C4B0; font-size: 11px; margin: 0;">
                Botão não funciona? Cole este link no navegador:<br>
                <a href="{magic_link}" style="color: #2A4B4A; word-break: break-all;">{magic_link}</a>
            </p>
        </div>
    </body>
    </html>
    """
    
 
def _build_invite_email(group_name: str, invited_by: str, magic_link: str) -> str:
    """Template HTML para e-mail de convite para grupo."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Inter, -apple-system, sans-serif; background: #F5F0E8; padding: 24px; margin: 0;">
        <div style="max-width: 480px; margin: 0 auto; background: #FFFFFF; border-radius: 12px; padding: 40px 32px; text-align: center; border: 1px solid #D9C4B0;">
            <!-- Ícone de convite -->
            <div style="margin-bottom: 24px;">
                <span style="font-size: 40px;">🤝</span>
            </div>
            
            <h1 style="color: #2A4B4A; font-size: 22px; font-weight: 600; margin: 0 0 8px 0;">
                Você foi convidado!
            </h1>
            
            <p style="color: #2A4B4A; font-size: 16px; line-height: 1.6; margin: 0 0 16px 0;">
                <strong style="color: #D9B382;">{invited_by}</strong> convidou você para participar do grupo
            </p>
            
            <!-- Card do grupo -->
            <div style="background: #F5F0E8; border: 1px solid #D9C4B0; border-radius: 8px; padding: 16px; margin: 0 0 24px 0;">
                <p style="color: #2A4B4A; font-size: 18px; font-weight: 500; margin: 0;">
                    🌙 {group_name}
                </p>
            </div>
            
            <p style="color: #2A4B4A; font-size: 14px; line-height: 1.6; margin: 0 0 24px 0;">
                Clique no botão abaixo para aceitar o convite e começar a compartilhar listas de compras.
            </p>
            
            <a href="{magic_link}" 
               style="display: inline-block; background: #2A4B4A; color: #F5F0E8; padding: 14px 40px; border-radius: 32px; text-decoration: none; font-weight: 500; font-size: 16px; margin: 8px 0;">
                Aceitar convite ✦
            </a>
            
            <p style="color: #8BA7B8; font-size: 12px; margin: 24px 0 0 0; line-height: 1.5;">
                Este convite expira em {settings.magic_link_expire_minutes} minutos.<br>
                Se você não conhece {invited_by}, ignore este e-mail.
            </p>
            
            <hr style="border: none; border-top: 1px solid #D9C4B0; margin: 24px 0;">
            
            <p style="color: #D9C4B0; font-size: 11px; margin: 0;">
                Botão não funciona? Cole este link no navegador:<br>
                <a href="{magic_link}" style="color: #2A4B4A; word-break: break-all;">{magic_link}</a>
            </p>
        </div>
    </body>
    </html>
    """
