import os
import logging
from telegram import Update, Document, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv
import mimetypes

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create uploads directory
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# ============ START COMMAND ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    welcome_text = f"""
🎉 Welcome {user.first_name}!

📁 I'm a File Sharing Bot. You can:
✅ Upload files
✅ Download files
✅ Share files with others
✅ Manage your files

Use /help to see all commands
    """
    
    keyboard = [
        [InlineKeyboardButton("📤 Upload File", callback_data='upload'),
         InlineKeyboardButton("📥 Download", callback_data='download')],
        [InlineKeyboardButton("📋 View Files", callback_data='list'),
         InlineKeyboardButton("🗑️ Delete", callback_data='delete')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# ============ HELP COMMAND ============
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
📚 **Available Commands:**

/start - Start the bot
/help - Show this message
/upload - Upload a file
/list - View all files
/delete - Delete a file
/info - Bot information
/status - Check bot status

**How to use:**
1️⃣ Send /upload
2️⃣ Select a file from your device
3️⃣ File will be saved and you get a download link
4️⃣ Share the link with anyone!

**File Limits:**
- Max size: 50 MB
- Supported: PDF, DOC, DOCX, TXT, XLSX, JPG, PNG, ZIP
    """
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# ============ UPLOAD FILE HANDLER ============
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads"""
    user = update.effective_user
    document = update.message.document
    
    try:
        # Check file size (50 MB limit)
        if document.file_size > 50 * 1024 * 1024:
            await update.message.reply_text(
                "❌ File too large! Max 50 MB allowed."
            )
            return
        
        # Get file extension
        file_name = document.file_name
        file_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
        
        # Check file type
        allowed_formats = ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'jpg', 'png', 'zip', 'mp4', 'mp3']
        if file_ext not in allowed_formats:
            await update.message.reply_text(
                f"❌ File type .{file_ext} not supported!\n"
                f"✅ Supported: {', '.join(allowed_formats)}"
            )
            return
        
        # Download and save file
        file = await context.bot.get_file(document.file_id)
        file_path = f"uploads/{user.id}_{file_name}"
        await file.download_to_drive(file_path)
        
        # Send confirmation with download link
        success_text = f"""
✅ **File Uploaded Successfully!**

📄 **File Name:** `{file_name}`
💾 **Size:** `{document.file_size / 1024:.2f} KB`
👤 **Owner:** `{user.first_name}`
🆔 **File ID:** `{document.file_id}`

**Download Link:**
`/download_{document.file_id}`

**Share this command with anyone:**
`/getfile_{document.file_id}`
        """
        await update.message.reply_text(success_text, parse_mode=ParseMode.MARKDOWN)
        
        # Log the upload
        logger.info(f"File uploaded: {file_name} by {user.first_name}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error uploading file: {str(e)}")
        logger.error(f"Upload error: {str(e)}")

# ============ LIST FILES COMMAND ============
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all uploaded files"""
    user = update.effective_user
    user_folder = f"uploads/{user.id}"
    
    try:
        if not os.path.exists(user_folder):
            await update.message.reply_text("📂 No files uploaded yet!")
            return
        
        files = os.listdir(user_folder)
        if not files:
            await update.message.reply_text("📂 Your uploads folder is empty!")
            return
        
        file_list = "📁 **Your Files:**\n\n"
        for i, file in enumerate(files, 1):
            file_path = os.path.join(user_folder, file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            file_list += f"{i}. `{file}` ({file_size:.2f} KB)\n"
        
        await update.message.reply_text(file_list, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ Error listing files: {str(e)}")

# ============ DELETE FILE COMMAND ============
async def delete_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a file"""
    await update.message.reply_text(
        "📝 Send the filename you want to delete:\n"
        "(Use /list to see your files)"
    )

# ============ INFO COMMAND ============
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot information"""
    info_text = """
ℹ️ **Bot Information**

**Name:** 📁 File Sharing Bot
**Version:** 1.0.0
**Features:** Upload, Download, Share Files
**Max File Size:** 50 MB
**Storage:** Cloud-based

**Developed By:** Your Name
**GitHub:** https://github.com/yourusername/telegram-file-sharing-bot

**Contact:** @YourTelegramUsername
    """
    await update.message.reply_text(info_text, parse_mode=ParseMode.MARKDOWN)

# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

# ============ MAIN FUNCTION ============
async def main():
    """Start the bot"""
    print("🚀 Bot starting...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("delete", delete_file))
    application.add_handler(CommandHandler("info", info_command))
    
    # File handler
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start polling
    print("✅ Bot is running... Press Ctrl+C to stop")
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
