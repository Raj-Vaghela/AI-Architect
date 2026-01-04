# PowerShell script to chat with Stack8s AI Architect
# Usage: .\scripts\chat_example.ps1

$BaseUrl = "http://localhost:8000/api/v1"

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Stack8s AI Architect - Chat Demo" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Start a conversation
Write-Host "Step 1: Starting conversation..." -ForegroundColor Yellow
$startResponse = Invoke-RestMethod -Uri "$BaseUrl/chat/start" -Method Post -ContentType "application/json"
$conversationId = $startResponse.conversation_id
Write-Host "✓ Conversation ID: $conversationId`n" -ForegroundColor Green

# Step 2: Send a message
Write-Host "Step 2: Sending message..." -ForegroundColor Yellow
$message = @{
    conversation_id = $conversationId
    message = "I need to deploy an LLM for inference, something like Llama 70B"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$BaseUrl/chat/message" -Method Post -Body $message -ContentType "application/json"

Write-Host "`nAI Response Type: $($response.response_type)" -ForegroundColor Cyan
Write-Host "`n--- AI Response ---" -ForegroundColor Cyan
Write-Host $response.response -ForegroundColor White
Write-Host "-------------------`n" -ForegroundColor Cyan

# If deployment plan exists
if ($response.deployment_plan) {
    Write-Host "✓ Deployment Plan Generated!" -ForegroundColor Green
    Write-Host "  - GPU Recommendations: $($response.deployment_plan.gpu_recommendations.Count)" -ForegroundColor White
    Write-Host "  - Model Recommendations: $($response.deployment_plan.model_recommendations.Count)" -ForegroundColor White
    Write-Host "  - K8s Packages: $($response.deployment_plan.kubernetes_stack.Count)`n" -ForegroundColor White
}

# Step 3: Get conversation history
Write-Host "Step 3: Fetching conversation history..." -ForegroundColor Yellow
$history = Invoke-RestMethod -Uri "$BaseUrl/chat/$conversationId" -Method Get

Write-Host "✓ Total messages: $($history.messages.Count)`n" -ForegroundColor Green

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Demo complete!" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "Your conversation ID: $conversationId" -ForegroundColor Yellow
Write-Host "`nTo continue chatting, use:" -ForegroundColor White
Write-Host "  python scripts\chat.py`n" -ForegroundColor Cyan

