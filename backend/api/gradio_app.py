import requests
import json
import gradio as gr

API_ENDPOINT = "http://127.0.0.1:8000/analyze"

class GradioUI:
    def analyze(self, image_url: str):
        if not image_url:
            return "", "Empty URL"

        if not image_url.startswith("http"):
            image_url = "https://" + image_url

        try:
            resp = requests.get(
                f"{API_ENDPOINT}/{image_url}",
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()

        except Exception as e:
            return (
                self._image_box(image_url),
                f"<pre style='color:red;'>ERROR: {str(e)}</pre>"
            )

        return self._image_box(image_url), self._render_analysis(data)

    def _image_box(self, image_url: str) -> str:
        return f"""
        <div style="
            border: 2px solid #444;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background-color: #111;
        ">
            <img src="{image_url}"
                 style="max-width:100%; max-height:400px; border-radius:6px;">
        </div>
        """

    # ANALYSIS RENDERER 
    def _render_analysis(self, data: dict) -> str:
        vd = data.get("visual_dimensions", {})
        va = data.get("visual_attributes", {})
        vm = data.get("visual_metadata", {})
        ambiguities = data.get("ambiguities", [])

        html = "<div style='padding:10px;'>"

        # Visual Dimensions
        html += "<h3>Visual Dimensions</h3>"
        for name, obj in vd.items():
            title = name.replace("_", " ").title()
            html += f"""
            <div style="
                border:1px solid #333;
                border-radius:8px;
                padding:10px;
                margin-bottom:10px;
                background:#181818;
            ">
                <b>{title}</b><br>
                Score: <b>{obj['score']}</b> &nbsp;|&nbsp;
                Confidence: <b>{obj['confidence']}</b><br>
                <i>{obj['reasoning']}</i>
            </div>
            """

        #  Visual Attributes 
        html += "<h3>Visual Attributes</h3><ul>"
        for k, v in va.items():
            label = k.replace("_", " ").title()
            if isinstance(v, list):
                v = ", ".join(v)
            html += f"<li><b>{label}:</b> {v}</li>"
        html += "</ul>"

        # Visual Metadata 
        html += "<h3>Visual Metadata</h3><ul>"
        for k, v in vm.items():
            label = k.replace("_", " ").title()
            html += f"<li><b>{label}:</b> {v}</li>"
        html += "</ul>"

        # ---- Ambiguities ----
        if ambiguities:
            html += "<h3>Ambiguities</h3><ul>"
            for a in ambiguities:
                html += f"<li>{a}</li>"
            html += "</ul>"

        html += "</div>"
        return html

    # Complete UI
    def run(self):
        with gr.Blocks() as app:
            gr.Markdown("## 🕶️ Eyeglasses Visual Analyzer")

            with gr.Row():
                # LHS
                with gr.Column(scale=1):
                    url_input = gr.Textbox(
                        label="Image URL",
                        placeholder="static5.lenskart.com/media/catalog/..."
                    )
                    analyze_btn = gr.Button("Analyze")
                    image_display = gr.HTML(label="Image Preview")

                # RHS
                with gr.Column(scale=1):
                    analysis_output = gr.HTML(
                        label="Analysis Output"
                    )

            analyze_btn.click(
                fn=self.analyze,
                inputs=url_input,
                outputs=[image_display, analysis_output]
            )

        app.launch(server_name="0.0.0.0",server_port=7860,share=False)


if __name__ == "__main__":
    GradioUI().run()
