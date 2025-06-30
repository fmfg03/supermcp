"""
Telegram Adapter for Proposal Evaluator Service
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from main import ProposalEvaluator, ProposalContext
from utils.logger import setup_logger
from utils.config import load_config

logger = setup_logger(__name__)

class ProposalEvaluatorBot:
    """
    Telegram bot interface for the proposal evaluator service
    """
    
    def __init__(self, config_path: str = "config/proposal_evaluator.yaml"):
        self.config = load_config(config_path)
        self.bot_token = self.config["telegram"]["bot_token"]
        self.allowed_users = set(self.config["telegram"].get("allowed_users", []))
        
        self.evaluator = ProposalEvaluator(config_path)
        
        # Initialize bot application
        self.application = Application.builder().token(self.bot_token).build()
        self._setup_handlers()
        
        # Active evaluations (to track ongoing processes)
        self.active_evaluations: Dict[int, Dict[str, Any]] = {}
    
    def _setup_handlers(self):
        """Set up bot command and message handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("evaluate", self.evaluate_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("cancel", self.cancel_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        
        # Document handler for context files
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self.document_handler)
        )
        
        # Text message handler
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        welcome_message = """🚀 **SuperMCP Proposal Evaluator Bot**

I can help you generate and refine business proposals using AI agents!

**Commands:**
/evaluate - Start a new proposal evaluation
/status - Check ongoing evaluations
/list - List recent proposals
/cancel - Cancel current evaluation
/help - Show this help message

**How it works:**
1. Use /evaluate to start
2. Provide client name and context
3. Upload context files if needed
4. Get AI-generated proposals refined by CFO/CMO/CEO perspectives
5. Receive final proposal + justification

Let's create some winning proposals! 💼"""

        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """📋 **Proposal Evaluator Help**

**Basic Usage:**
```
/evaluate GlobalTown "Increase revenue by 20%"
```

**With Context File:**
1. Upload a .txt or .md file with context
2. Use /evaluate with client name
3. The bot will use the uploaded context

**Advanced Options:**
- Add multiple objectives separated by commas
- Use parallel evaluation for aggressive vs diplomatic tones
- Download results as files

**Examples:**
```
/evaluate "TechCorp" "Digital transformation, Cost reduction"
/evaluate "StartupXYZ" --parallel
```

**Features:**
✅ Multi-agent evaluation (CFO/CMO/CEO)
✅ Iterative refinement (up to 5 rounds)
✅ Supabase persistence
✅ File downloads (proposal + justification)
✅ Parallel variant testing"""

        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def evaluate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /evaluate command"""
        user_id = update.effective_user.id
        
        # Check authorization
        if self.allowed_users and user_id not in self.allowed_users:
            await update.message.reply_text("❌ Unauthorized. Contact admin for access.")
            return
        
        # Parse command arguments
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ Usage: /evaluate <client_name> [objectives]\n\n"
                "Example: /evaluate \"GlobalTown\" \"Increase revenue, Reduce costs\""
            )
            return
        
        client_name = args[0].strip('"')
        objectives = []
        
        if len(args) > 1:
            objectives_text = " ".join(args[1:]).strip('"')
            objectives = [obj.strip() for obj in objectives_text.split(",")]
        
        # Check for uploaded context
        context_text = self.active_evaluations.get(user_id, {}).get("context", "")
        if not context_text:
            context_text = "No specific context provided. Please analyze general business improvement opportunities."
        
        # Start evaluation
        await self._start_evaluation(update, client_name, context_text, objectives)
    
    async def _start_evaluation(
        self, 
        update: Update, 
        client_name: str, 
        context_text: str, 
        objectives: list[str]
    ):
        """Start proposal evaluation process"""
        user_id = update.effective_user.id
        
        # Set default objectives if none provided
        if not objectives:
            objectives = ["Increase revenue", "Reduce costs", "Improve efficiency"]
        
        # Create context object
        proposal_context = ProposalContext(
            client=client_name,
            context=context_text,
            objectives=objectives
        )
        
        # Track evaluation
        self.active_evaluations[user_id] = {
            "status": "running",
            "client": client_name,
            "start_time": asyncio.get_event_loop().time()
        }
        
        # Send starting message
        status_message = await update.message.reply_text(
            f"🚀 **Starting evaluation for {client_name}**\n\n"
            f"📋 Objectives: {', '.join(objectives)}\n"
            f"🤖 Agents: BuilderAgent → JudgeAgent → RefinerAgent\n"
            f"⏱️ Estimated time: 2-5 minutes\n\n"
            f"*Please wait while I generate and refine your proposal...*",
            parse_mode='Markdown'
        )
        
        try:
            # Run evaluation
            result = await self.evaluator.evaluate_proposal(proposal_context)
            
            # Update status
            self.active_evaluations[user_id]["status"] = "completed"
            self.active_evaluations[user_id]["result"] = result
            
            # Send results
            await self._send_evaluation_results(update, result, status_message)
            
        except Exception as e:
            logger.error(f"Evaluation failed for user {user_id}: {e}")
            
            # Update status
            self.active_evaluations[user_id]["status"] = "failed"
            self.active_evaluations[user_id]["error"] = str(e)
            
            await status_message.edit_text(
                f"❌ **Evaluation failed for {client_name}**\n\n"
                f"Error: {str(e)}\n\n"
                f"Please try again or contact support.",
                parse_mode='Markdown'
            )
    
    async def _send_evaluation_results(self, update: Update, result, status_message):
        """Send evaluation results to user"""
        
        # Edit status message with summary
        summary_text = f"""✅ **Evaluation Complete for {result.client}**

📊 **Final Score:** {result.final_score:.1f}/10
🔄 **Iterations:** {len(result.iterations)}
📈 **Improvement:** +{result.iterations[-1].overall_score - result.iterations[0].overall_score:.1f} points

**Key Metrics:**
• CFO Perspective: {[e for e in result.iterations[-1].evaluations if e.perspective == 'CFO'][0].score:.1f}/10
• CMO Perspective: {[e for e in result.iterations[-1].evaluations if e.perspective == 'CMO'][0].score:.1f}/10  
• CEO Perspective: {[e for e in result.iterations[-1].evaluations if e.perspective == 'CEO'][0].score:.1f}/10

*Sending files...*"""

        await status_message.edit_text(summary_text, parse_mode='Markdown')
        
        # Send proposal file
        proposal_content = f"# Proposal for {result.client}\n\n{result.final_proposal}"
        await self._send_text_file(
            update, 
            proposal_content, 
            f"{result.client}_proposal.md",
            "📄 **Final Proposal**"
        )
        
        # Send justification file
        await self._send_text_file(
            update,
            result.justification,
            f"{result.client}_justification.txt", 
            "📋 **Evaluation Justification**"
        )
        
        # Send detailed JSON result
        result_json = json.dumps({
            "client": result.client,
            "final_score": result.final_score,
            "iterations": len(result.iterations),
            "metadata": result.metadata
        }, indent=2)
        
        await self._send_text_file(
            update,
            result_json,
            f"{result.client}_summary.json",
            "📊 **Evaluation Summary**"
        )
    
    async def _send_text_file(self, update: Update, content: str, filename: str, caption: str):
        """Send text content as a file"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=filename,
                    caption=caption,
                    parse_mode='Markdown'
                )
        finally:
            Path(temp_path).unlink()  # Clean up temp file
    
    async def document_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle uploaded documents (context files)"""
        user_id = update.effective_user.id
        document: Document = update.message.document
        
        # Check file type
        if not document.file_name.endswith(('.txt', '.md')):
            await update.message.reply_text(
                "❌ Please upload .txt or .md files only."
            )
            return
        
        try:
            # Download file
            file = await context.bot.get_file(document.file_id)
            file_content = await file.download_as_bytearray()
            context_text = file_content.decode('utf-8')
            
            # Store context for user
            if user_id not in self.active_evaluations:
                self.active_evaluations[user_id] = {}
            
            self.active_evaluations[user_id]["context"] = context_text
            
            await update.message.reply_text(
                f"✅ **Context uploaded successfully!**\n\n"
                f"📄 File: {document.file_name}\n"
                f"📏 Size: {len(context_text)} characters\n\n"
                f"Now use: `/evaluate \"ClientName\" \"objectives\"`",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            await update.message.reply_text(
                f"❌ Failed to process document: {str(e)}"
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        
        if user_id not in self.active_evaluations:
            await update.message.reply_text("📭 No active evaluations.")
            return
        
        evaluation = self.active_evaluations[user_id]
        status = evaluation.get("status", "unknown")
        
        if status == "running":
            elapsed = asyncio.get_event_loop().time() - evaluation["start_time"]
            await update.message.reply_text(
                f"⏳ **Evaluation in progress**\n\n"
                f"Client: {evaluation['client']}\n"
                f"Elapsed: {elapsed:.0f} seconds\n"
                f"Status: Running agents..."
            )
        elif status == "completed":
            result = evaluation["result"]
            await update.message.reply_text(
                f"✅ **Last evaluation completed**\n\n"
                f"Client: {result.client}\n"
                f"Score: {result.final_score:.1f}/10\n"
                f"Iterations: {len(result.iterations)}"
            )
        elif status == "failed":
            await update.message.reply_text(
                f"❌ **Last evaluation failed**\n\n"
                f"Client: {evaluation['client']}\n"
                f"Error: {evaluation.get('error', 'Unknown error')}"
            )
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cancel command"""
        user_id = update.effective_user.id
        
        if user_id in self.active_evaluations:
            del self.active_evaluations[user_id]
            await update.message.reply_text("✅ Evaluation cancelled.")
        else:
            await update.message.reply_text("📭 No active evaluation to cancel.")
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        try:
            # Get recent proposals from database
            response = self.evaluator.supabase.table("proposals").select(
                "client, score, timestamp"
            ).order("timestamp", desc=True).limit(10).execute()
            
            if not response.data:
                await update.message.reply_text("📭 No proposals found.")
                return
            
            list_text = "📋 **Recent Proposals:**\n\n"
            for proposal in response.data:
                list_text += f"• {proposal['client']} - {proposal['score']:.1f}/10 - {proposal['timestamp'][:10]}\n"
            
            await update.message.reply_text(list_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Failed to list proposals: {e}")
            await update.message.reply_text("❌ Failed to retrieve proposals.")
    
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (for natural language commands)"""
        text = update.message.text.lower()
        
        if "propuesta" in text or "proposal" in text:
            await update.message.reply_text(
                "💡 To generate a proposal, use:\n"
                "`/evaluate \"ClientName\" \"objectives\"`\n\n"
                "Upload context files first if needed!",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🤖 Use /help to see available commands."
            )
    
    def run(self):
        """Run the Telegram bot"""
        logger.info("Starting Proposal Evaluator Telegram Bot...")
        self.application.run_polling()

if __name__ == "__main__":
    bot = ProposalEvaluatorBot()
    bot.run()