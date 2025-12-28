import requests
import gradio as gr
import os

API_ENDPOINT = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/analyze")


class GradioUI:

    def analyze_bulk(self, csv_text: str):
        if not csv_text.strip():
            return "<pre style='color:red;'>Empty input</pre>"

        urls = [
            line.strip()
            for line in csv_text.splitlines()
            if line.strip()
        ]

        html = "<div style='padding:10px;'>"

        for idx, url in enumerate(urls, start=1):
            html += self._analyze_single(idx, url)

        html += "</div>"
        return html

    # ---------- SINGLE IMAGE ----------
    def _analyze_single(self, idx: int, image_url: str) -> str:
        if not image_url.startswith("http"):
            image_url = "https://" + image_url

        try:
            resp = requests.get(f"{API_ENDPOINT}/{image_url}")
            resp.raise_for_status()
            data = resp.json()
            analysis_html = self._render_analysis(data)

        except Exception as e:
            analysis_html = f"<pre style='color:red;'>ERROR: {str(e)}</pre>"

        return f"""
        <details style="
            margin-bottom:15px;
            border:1px solid #333;
            border-radius:10px;
            background:#121212;
        ">
          <summary style="
              cursor:pointer;
              padding:10px;
              font-weight:bold;
              background:#1a1a1a;
              border-radius:10px;
          ">
            Image {idx}
          </summary>

          <div style="padding:15px;">
            {self._image_box(image_url)}
            <hr style="border-color:#333;">
            {analysis_html}
          </div>
        </details>
        """

    # ---------- IMAGE BOX ----------
    def _image_box(self, image_url: str) -> str:
        return f"""
        <div style="
            border:2px solid #444;
            border-radius:10px;
            padding:10px;
            text-align:center;
            background:#111;
            margin-bottom:15px;
        ">
            <img src="{image_url}"
                 style="max-width:100%; max-height:360px; border-radius:6px;">
        </div>
        """

    # ---------- ANALYSIS RENDER ----------
    def _render_analysis(self, data: dict) -> str:
        vd = data.get("visual_dimensions", {})
        va = data.get("visual_attributes", {})
        vm = data.get("visual_metadata", {})
        ambiguities = data.get("ambiguities", [])

        html = "<div>"

        html += "<h3>Visual Dimensions</h3>"
        for name, obj in vd.items():
            html += f"""
            <div style="
                border:1px solid #333;
                border-radius:8px;
                padding:10px;
                margin-bottom:10px;
                background:#181818;
            ">
                <b>{name.replace('_',' ').title()}</b><br>
                Score: <b>{obj['score']}</b> |
                Confidence: <b>{obj['confidence']}</b><br>
                <i>{obj['reasoning']}</i>
            </div>
            """

        html += "<h3>Visual Attributes</h3><ul>"
        for k, v in va.items():
            if isinstance(v, list):
                v = ", ".join(v)
            html += f"<li><b>{k.replace('_',' ').title()}:</b> {v}</li>"
        html += "</ul>"

        html += "<h3>Visual Metadata</h3><ul>"
        for k, v in vm.items():
            html += f"<li><b>{k.replace('_',' ').title()}:</b> {v}</li>"
        html += "</ul>"

        if ambiguities:
            html += "<h3>Ambiguities</h3><ul>"
            for a in ambiguities:
                html += f"<li>{a}</li>"
            html += "</ul>"

        html += "</div>"
        return html

    # ---------- UI ----------
    def run(self):
        with gr.Blocks() as app:
            gr.Markdown("## 🕶️ Eyeglasses Visual Analyzer — Batch Mode")

            with gr.Row():

                # ---------- LEFT ----------
                with gr.Column(scale=1):
                    gr.Markdown("### Image Inputs")
                    csv_input = gr.Textbox(
                        label="Image URLs (one per line / CSV)",
                        placeholder="static5.lenskart.com/...\nhttps://...\n...",
                        lines=12
                    )
                    analyze_btn = gr.Button("Analyze Images")

                # ---------- RIGHT ----------
                with gr.Column(scale=2):
                    gr.Markdown("### Analysis Results")
                    output_html = gr.HTML()

            analyze_btn.click(
                fn=self.analyze_bulk,
                inputs=csv_input,
                outputs=output_html
            )

        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )


if __name__ == "__main__":
    GradioUI().run()
