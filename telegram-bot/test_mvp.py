"""
Test script for CogniCraft AI MVP
Tests the Gemini integration and HTML generation
"""

import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


async def test_gemini_connection():
    """Test basic Gemini API connection"""
    print("Testing Gemini API connection...")
    try:
        response = await model.generate_content_async("Say 'Hello, CogniCraft!'")
        print(f"✅ Gemini Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        return False


async def test_html_generation():
    """Test HTML generation"""
    print("\nTesting HTML generation...")
    
    test_content = "Welcome to CogniCraft AI - A powerful platform for creating interactive web experiences."
    test_style = "Quantum Void - space theme with purple gradients"
    
    prompt = f"""Create a simple single-file HTML page with this content and style:

CONTENT: {test_content}

STYLE: {test_style}

Requirements:
1. Single HTML file with embedded CSS
2. Use Tailwind CSS CDN
3. Apply the space theme with purple gradients
4. Add a centered card layout
5. Include a title and the content

Generate only the HTML code:"""

    try:
        response = await model.generate_content_async(prompt)
        html = response.text.strip()
        
        # Save test HTML
        with open("test_output.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        print("✅ HTML generated successfully!")
        print(f"✅ Saved to: test_output.html")
        print(f"✅ HTML Preview (first 200 chars): {html[:200]}...")
        return True
    except Exception as e:
        print(f"❌ HTML Generation Error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("🧠✨ CogniCraft AI MVP Test Suite\n")
    
    # Check environment
    print("Checking environment variables...")
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    print("✅ Environment variables loaded\n")
    
    # Run tests
    tests_passed = 0
    
    if await test_gemini_connection():
        tests_passed += 1
    
    if await test_html_generation():
        tests_passed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests completed: {tests_passed}/2 passed")
    
    if tests_passed == 2:
        print("✅ All tests passed! MVP is ready to use.")
        print("\nTo run the bot: python mvp.py")
    else:
        print("❌ Some tests failed. Please check your configuration.")


if __name__ == "__main__":
    asyncio.run(main())