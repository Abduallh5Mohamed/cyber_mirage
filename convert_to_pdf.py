"""
Convert Markdown files to PDF with proper formatting
"""
import markdown
from weasyprint import HTML, CSS
from pathlib import Path
import re

def convert_mermaid_to_image_placeholder(md_content):
    """Replace Mermaid diagrams with placeholder text"""
    # Find all mermaid code blocks
    pattern = r'```mermaid\n(.*?)```'
    
    def replace_mermaid(match):
        diagram_content = match.group(1)
        # Count lines to estimate diagram size
        lines = diagram_content.strip().split('\n')
        diagram_type = lines[0].strip() if lines else "diagram"
        return f'\n\n**[{diagram_type.upper()} DIAGRAM - See original Markdown file for interactive visualization]**\n\n'
    
    return re.sub(pattern, replace_mermaid, md_content, flags=re.DOTALL)

def markdown_to_pdf(md_file, output_pdf):
    """Convert Markdown to PDF"""
    print(f"Converting {md_file} to {output_pdf}...")
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Replace Mermaid diagrams (they can't render in PDF directly)
    md_content = convert_mermaid_to_image_placeholder(md_content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.meta',
    ])
    
    html_content = md.convert(md_content)
    
    # Create complete HTML document with styling
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                margin: 2cm;
                size: A4;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                }}
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                color: #1a1a1a;
                font-size: 24pt;
                margin-top: 1cm;
                margin-bottom: 0.5cm;
                page-break-before: auto;
                border-bottom: 3px solid #2c3e50;
                padding-bottom: 8pt;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 18pt;
                margin-top: 0.8cm;
                margin-bottom: 0.4cm;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5pt;
            }}
            h3 {{
                color: #34495e;
                font-size: 14pt;
                margin-top: 0.6cm;
                margin-bottom: 0.3cm;
            }}
            h4 {{
                color: #555;
                font-size: 12pt;
                margin-top: 0.4cm;
                margin-bottom: 0.2cm;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
                font-size: 10pt;
            }}
            table, th, td {{
                border: 1px solid #ddd;
            }}
            th {{
                background-color: #3498db;
                color: white;
                padding: 8pt;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                padding: 6pt;
                text-align: left;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2pt 4pt;
                border-radius: 3pt;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            pre {{
                background-color: #f8f8f8;
                padding: 10pt;
                border-left: 4px solid #3498db;
                overflow-x: auto;
                font-size: 9pt;
                line-height: 1.4;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #ccc;
                padding-left: 1em;
                margin-left: 0;
                color: #666;
                font-style: italic;
            }}
            ul, ol {{
                margin-left: 1.5em;
            }}
            li {{
                margin-bottom: 0.3em;
            }}
            strong {{
                color: #2c3e50;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            .page-break {{
                page-break-after: always;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    HTML(string=full_html).write_pdf(output_pdf)
    print(f"✓ Created: {output_pdf}")

if __name__ == "__main__":
    # Define artifact directory
    artifact_dir = Path(r"C:\Users\abdua\.gemini\antigravity\brain\33b88397-dc90-4d0b-85e1-a305170e3a7a")
    
    # Convert both documents
    files_to_convert = [
        ("problem_formulation.md", "Problem_Formulation_IEEE_Style.pdf"),
        ("system_architecture.md", "System_Architecture_Design.pdf")
    ]
    
    for md_file, pdf_file in files_to_convert:
        md_path = artifact_dir / md_file
        pdf_path = artifact_dir / pdf_file
        
        if md_path.exists():
            markdown_to_pdf(str(md_path), str(pdf_path))
        else:
            print(f"✗ File not found: {md_path}")
    
    print("\n✅ PDF conversion complete!")
    print(f"\nPDF files saved in: {artifact_dir}")
