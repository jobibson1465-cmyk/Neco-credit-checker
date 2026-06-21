from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
<title>NECO Credit Checker - MEXT</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:Arial;max-width:600px;margin:50px auto;padding:20px;background:#f5f5f5}
.container{background:white;padding:30px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
h1{color:#2c3e50;text-align:center}
input,button{width:100%;padding:12px;margin:10px 0;border:2px solid #3498db;border-radius:5px;font-size:16px}
button{background:#3498db;color:white;border:none;cursor:pointer;font-weight:bold}
button:hover{background:#2980b9}
.result{margin-top:20px;padding:15px;border-radius:5px;display:none}
.success{background:#d4edda;color:#155724;border:1px solid #c3e6cb}
.error{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}
</style>
</head>
<body>
<div class="container">
<h1>NECO Credit Checker</h1>
<p><b>MEXT Requirement:</b> 20 units + Pass in English & Math</p>
<input type="text" id="courses" placeholder="Enter courses: ENG101,MAT101,CSC101,CSC102...">
<button onclick="checkCredits()">Check Eligibility</button>
<div id="result" class="result"></div>
</div>
<script>
async function checkCredits(){
const courses = document.getElementById('courses').value;
const resultDiv = document.getElementById('result');
const res = await fetch('/check', {
method: 'POST',
headers: {'Content-Type': 'application/json'},
body: JSON.stringify({courses: courses})
});
const data = await res.json();
resultDiv.style.display = 'block';
resultDiv.className = data.pass ? 'result success' : 'result error';
resultDiv.innerHTML = `<b>${data.message}</b><br>Total Credits: ${data.total_credits}`;
}
</script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    courses = data.get('courses', '')
    
    course_list = [c.strip().upper() for c in courses.split(',') if c.strip()]
    total_credits = len(course_list) * 4
    
    has_english = any('ENG' in c for c in course_list)
    has_math = any('MAT' in c for c in course_list)
    
    passed = total_credits >= 20 and has_english and has_math
    
    if passed:
        message = "✅ ELIGIBLE for MEXT! You have 20+ credits + Pass in English & Math"
    else:
        missing = []
        if total_credits < 20: missing.append(f"Need {20-total_credits} more credits")
        if not has_english: missing.append("Missing English course")
        if not has_math: missing.append("Missing Math course")
        message = f"❌ NOT ELIGIBLE: {', '.join(missing)}"
    
    return jsonify({
        'pass': passed,
        'total_credits': total_credits,
        'message': message,
        'has_english': has_english,
        'has_math': has_math
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
