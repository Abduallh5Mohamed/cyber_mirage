"""
Convert Markdown to HTML with WORKING Mermaid diagram support
"""
import markdown
from pathlib import Path
import re

def process_markdown_with_mermaid(md_content):
    """Process markdown converting mermaid blocks directly to HTML divs"""
    
    def mermaid_to_div(match):
        diagram_code = match.group(1).strip()
        # Return proper HTML div that Mermaid.js can process
        return f'\n<div class="mermaid">\n{diagram_code}\n</div>\n'
    
    # Replace ```mermaid blocks BEFORE markdown processing
    md_content = re.sub(
        r'```mermaid\n(.*?)\n```',
        mermaid_to_div,
        md_content,
        flags=re.DOTALL | re.MULTILINE
    )
    
    return md_content

def markdown_to_html_with_mermaid(md_file, output_html):
    """Convert Markdown to styled HTML with Mermaid support"""
    print(f"Converting {md_file} to {output_html}...")
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Process Mermaid blocks FIRST
    md_content = process_markdown_with_mermaid(md_content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
    ])
    
    html_body = md.convert(md_content)
    
    # Get title from filename
    title = Path(md_file).stem.replace('_', ' ').title()
    
    # Create complete HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- Mermaid JS CDN -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            themeVariables: {{
                primaryColor: '#3498db',
                primaryTextColor: '#2c3e50',
                primaryBorderColor: '#2c3e50',
                lineColor: '#34495e',
                secondaryColor: '#e74c3c',
                tertiaryColor: '#f39c12'
            }}
        }});
    </script>
    
    <style>
        * {{ box-sizing: border-box; }}
        
        @page {{
            margin: 2cm;
            size: A4;
        }}
        
        @media print {{
            body {{ font-size: 11pt; }}
            h1 {{ page-break-before: always; }}
            h1:first-of-type {{ page-break-before: auto; }}
            h1, h2, h3, h4, h5, h6 {{ page-break-after: avoid; }}
            table, figure, .mermaid {{ page-break-inside: avoid; }}
            .no-print {{ display: none !important; }}
        }}
        
        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            line-height: 1.7;
            color: #333;
            max-width: 21cm;
            margin: 0 auto;
            padding: 2cm;
            background: #fff;
        }}
        
        h1 {{
            color: #1a1a1a;
            font-size: 28pt;
            margin-top: 1.5cm;
            margin-bottom: 0.8cm;
            border-bottom: 4px solid #2c3e50;
            padding-bottom: 10pt;
            font-weight: 700;
        }}
        
        h2 {{
            color: #2c3e50;
            font-size: 20pt;
            margin-top: 1.2cm;
            margin-bottom: 0.6cm;
            border-bottom: 3px solid #3498db;
            padding-bottom: 8pt;
            font-weight: 600;
        }}
        
        h3 {{
            color: #34495e;
            font-size: 16pt;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            font-weight: 600;
        }}
        
        h4 {{
            color: #555;
            font-size: 14pt;
            margin-top: 0.6cm;
            margin-bottom: 0.3cm;
            font-weight: 600;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5em 0;
            font-size: 10pt;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 12pt;
            text-align: left;
            font-weight: 600;
            border: 1px solid #5a67d8;
        }}
        
        td {{
            padding: 10pt;
            border: 1px solid #e0e0e0;
        }}
        
        tbody tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tbody tr:hover {{ background-color: #e9ecef; }}
        
        code {{
            background-color: #f5f5f5;
            padding: 3pt 6pt;
            border-radius: 4pt;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            color: #d63384;
            border: 1px solid #ececec;
        }}
        
        pre {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 15pt;
            border-left: 5px solid #3498db;
            overflow-x: auto;
            border-radius: 6pt;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1.5em 0;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
            border: none;
            color: #2d3748;
            font-size: 10pt;
            line-height: 1.5;
        }}
        
        /* Mermaid diagram styling */
        .mermaid {{
            background-color: #fafafa;
            border: 2px solid #3498db;
            border-radius: 8pt;
            padding: 20pt;
            margin: 2em 0;
            text-align: center;
            page-break-inside: avoid;
            min-height: 100px;
        }}
        
        ul, ol {{ margin-left: 2em; margin-bottom: 1em; }}
        li {{ margin-bottom: 0.5em; line-height: 1.6; }}
        
        blockquote {{
            border-left: 5px solid #e74c3c;
            padding-left: 1.5em;
            margin-left: 0;
            margin-right: 0;
            color: #555;
            font-style: italic;
            background-color: #fef5f5;
            padding: 1em 1em 1em 1.5em;
            border-radius: 0 6pt 6pt 0;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
            border-bottom: 1px dotted #3498db;
        }}
        
        a:hover {{
            color: #2980b9;
            border-bottom: 1px solid #2980b9;
        }}
        
        strong {{ color: #2c3e50; font-weight: 600; }}
        em {{ color: #555; }}
        
        .no-print {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14pt;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            z-index: 1000;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-weight: 600;
        }}
        
        .no-print:hover {{
            background: #229954;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.3);
        }}
        
        .document-header {{
            text-align: center;
            margin-bottom: 2cm;
            padding-bottom: 1cm;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .document-title {{
            font-size: 32pt;
            color: #2c3e50;
            margin-bottom: 0.5cm;
            font-weight: 700;
        }}
        
        .document-subtitle {{
            font-size: 14pt;
            color: #7f8c8d;
            font-weight: 400;
        }}
        
        #status {{
            text-align: center;
            padding: 15pt;
            background: #d4edda;
            border: 2px solid #28a745;
            border-radius: 6pt;
            color: #155724;
            font-weight: 600;
            margin: 20pt 0;
        }}
    </style>
</head>
<body>
    <button class="no-print" onclick="window.print()">🖨️ إطبع / احفظ PDF</button>
    
    <div class="document-header">
        <div class="document-title">{title}</div>
        <div class="document-subtitle">Cyber Mirage AI-Powered Honeypot System</div>
    </div>
    
    <div id="status" class="no-print">
        ⏳ جاري تحميل المخططات...
    </div>
    
    {html_body}
    
    <script>
        // Wait for all diagrams to render
        setTimeout(function() {{
            const diagrams = document.querySelectorAll('.mermaid svg');
            const status = document.getElementById('status');
            if (status) {{
                if (diagrams.length > 0) {{
                    status.innerHTML = '✅ تم تحميل ' + diagrams.length + ' مخطط بنجاح!';
                    status.style.background = '#d4edda';
                    setTimeout(() => status.style.display = 'none', 3000);
                }} else {{
                    status.innerHTML = '⚠️ لم يتم العثور على مخططات';
                    status.style.background = '#fff3cd';
                    status.style.borderColor = '#ffc107';
                }}
            }}
        }}, 2500);
    </script>
</body>
</html>"""
    
    # Write HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    # Count mermaid divs
    mermaid_count = html_body.count('<div class="mermaid">')
    print(f"✓ Created: {output_html}")
    print(f"  → Found {mermaid_count} Mermaid diagrams")

if __name__ == "__main__":
    artifact_dir = Path(r"C:\Users\abdua\.gemini\antigravity\brain\33b88397-dc90-4d0b-85e1-a305170e3a7a")
    
    files_to_convert = [
        ("problem_formulation.md", "Problem_Formulation_IEEE_Style.html"),
        ("system_architecture.md", "System_Architecture_Design.html")
    ]
    
    print("=" * 60)
    print("Converting Markdown to HTML with Mermaid Diagrams")
    print("=" * 60)
    print()
    
    for md_file, html_file in files_to_convert:
        md_path = artifact_dir / md_file
        html_path = artifact_dir / html_file
        
        if md_path.exists():
            markdown_to_html_with_mermaid(str(md_path), str(html_path))
            print()
        else:
            print(f"✗ File not found: {md_path}")
            print()
    
    print("=" * 60)
    print("✅ تم التحويل بنجاح!")
    print("=" * 60)
    print()
    print("خطوات الاستخدام:")
    print("  1. افتح ملف HTML في Chrome أو Edge")
    print("  2. انتظر ظهور رسالة 'تم تحميل المخططات'")
    print("  3. اضغط الزر الأخضر 'إطبع / احفظ PDF'")
    print("  4. اختر 'Save as PDF' واحفظ الملف")
