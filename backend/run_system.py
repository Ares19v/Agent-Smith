import gradio as gr

# VERSION 8.0 - GRADIO 6 COMPATIBLE
custom_css = '''
body, .gradio-container { background-color: #000000 !important; color: #ececf1 !important; margin: 0 !important; }

/* Sidebar */
.sidebar { border-right: 1px solid #1a1a1a !important; height: 100vh !important; display: flex !important; flex-direction: column !important; }
.sidebar-header { padding: 24px 20px 12px 20px; font-size: 14px; font-weight: 500; font-family: serif; }
.agent-item { padding: 8px 24px; font-size: 13px; color: #ececf1; cursor: pointer; }
.agent-item:hover { background-color: #1a1a1c !important; border-radius: 6px; margin: 0 10px; }
.sidebar-footer { margin-top: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; }
.create-btn { background: transparent !important; border: 1px solid #333 !important; color: #ececf1 !important; padding: 8px !important; border-radius: 6px !important; font-size: 13px !important; }
.signup-link { color: #666; font-size: 13px; text-decoration: none; padding-left: 10px; cursor: pointer; }

/* Workspace */
.main-workspace { height: 100vh !important; display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important; }
.content-wrapper { width: 100% !important; max-width: 720px !important; display: flex !important; flex-direction: column !important; }

/* Prompt Box */
.prompt-box { 
    background-color: #111113 !important; 
    border: 1px solid #2b2b2e !important; 
    border-radius: 14px !important; 
    padding: 8px 12px !important; 
    display: flex !important;
    flex-direction: column !important;
    min-height: 120px !important;
}
.prompt-input textarea { background-color: transparent !important; border: none !important; color: #ececf1 !important; font-size: 16px !important; resize: none !important; }

/* Toolbar Alignment */
.toolbar { display: flex !important; justify-content: space-between !important; align-items: center !important; margin-top: auto !important; padding: 5px 0 !important; }
.toolbar-right { display: flex !important; align-items: center !important; gap: 8px !important; }

.icon-btn { background: transparent !important; border: none !important; color: #666 !important; cursor: pointer !important; min-width: 35px !important; height: 35px !important; display: flex !important; justify-content: center !important; align-items: center !important; }
.icon-btn:hover { color: #fff !important; background-color: #2b2b30 !important; border-radius: 6px !important; }

.agent-select { background: transparent !important; border: none !important; min-width: 100px !important; }
.agent-select input { color: #666 !important; font-size: 13px !important; text-align: right !important; border: none !important; background: transparent !important; }
'''

# SVGs
plus_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>'
mic_svg = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>'

with gr.Blocks() as app:
    with gr.Row():
        with gr.Column(scale=2, elem_classes="sidebar"):
            gr.HTML('<div class="sidebar-header">Agent Smith</div>')
            gr.HTML('<div class="agent-item">Coder</div><div class="agent-item">Default Core</div>')
            with gr.Column(elem_classes="sidebar-footer"):
                gr.Button("+ Create Agents", elem_classes="create-btn")
                gr.HTML('<a class="signup-link">Sign Up</a>')
        
        with gr.Column(scale=8, elem_classes="main-workspace"):
            with gr.Column(elem_classes="content-wrapper"):
                gr.HTML('<div style="display:flex;justify-content:center;align-items:center;gap:12px;margin-bottom:20px;"><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M14.5 2H9.5L10.5 4H13.5L14.5 2Z" fill="#00a8ff"/><path d="M10.5 4L8 10L12 22L16 10L13.5 4H10.5Z" fill="#00a8ff"/></svg><h1 style="font-family:serif;font-size:2.4rem;font-weight:400;margin:0;color:#fff;">Afternoon, Dev</h1></div>')
                
                with gr.Column(elem_classes="prompt-box"):
                    gr.Textbox(show_label=False, placeholder="How can I help you today?", lines=2, elem_classes="prompt-input")
                    with gr.Row(elem_classes="toolbar"):
                        # Corrected positional arguments for buttons
                        gr.Button(plus_svg, elem_classes="icon-btn")
                        with gr.Row(elem_classes="toolbar-right"):
                            gr.Dropdown(choices=["Coder", "Default Core"], value="Coder", show_label=False, container=False, elem_classes="agent-select")
                            gr.Button(mic_svg, elem_classes="icon-btn")

if __name__ == '__main__':
    # Moved CSS and Theme here to comply with Gradio 6 rules
    app.launch(server_name="127.0.0.1", server_port=7862, theme=gr.themes.Base(), css=custom_css)