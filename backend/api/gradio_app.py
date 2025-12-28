import requests
import gradio as gr
import os
import json

# BACKEND_URL is when im using docker, and another fallback if for testing while deveoping on my machine
API_ENDPOINT = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/analyze") 


# the HTML beautufication was done by GPT (im not a frontend guy)
class GradioUI:
    def analyze_bulk(self, csv_text: str):
        if not csv_text.strip():
            return "<pre style='color:red;'>Empty input</pre>", "" 

        urls = [
            line.strip()
            for line in csv_text.splitlines()
            if line.strip()
        ]

        all_results = {}
        results_html = "<div style='padding:10px;'>"

        for idx, url in enumerate(urls, start=1):
            block_html, json_data = self._analyze_single(idx, url)
            results_html += block_html
            if json_data is not None:
                all_results[url] = json_data

        results_html += "</div>"

        # ALL JSON (on the LHS) 
        all_json_html = f"""
        <details style="
            margin-top:15px;
            border:2px solid #555;
            border-radius:10px;
            background:#0f0f0f;
        ">
          <summary style="
              cursor:pointer;
              padding:10px;
              font-weight:bold;
          ">
            View ALL Results JSON
          </summary>
          <pre style="white-space:pre-wrap;padding:12px;">
            {json.dumps(all_results, indent=2)}
          </pre>
        </details>
        """

        return all_json_html, results_html

    # SINGLE IMAGE  
    def _analyze_single(self, idx: int, image_url: str):
        if not image_url.startswith("http"): 
            # a simple check to ensure hyerlinks and direct urls, bith work
            image_url = "https://" + image_url

        try:
            resp = requests.get(f"{API_ENDPOINT}/{image_url}")
            resp.raise_for_status()
            data = resp.json()
            analysis_html = self._render_analysis(data)

            json_html = f"""
            <details style="margin-top:10px;">
              <summary style="cursor:pointer;"> View JSON</summary>
              <pre style="white-space:pre-wrap;">
                {json.dumps(data, indent=2)}
              </pre>
            </details>
            """

        except Exception as e:
            return (
                f"<pre style='color:red;'>Image {idx}: {str(e)}</pre>",
                None
            )

        block = f"""
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
          ">
            Image {idx}
          </summary>

          <div style="padding:15px;">
            {self._image_box(image_url)}
            <hr style="border-color:#333;">
            {analysis_html}
            {json_html}
          </div>
        </details>
        """

        return block, data

    # IMAGE BOX 
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

    # ANALYSIS (json -> simple words) (making json more readable for non-tech users)
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

    #  UI 
    def run(self):
        with gr.Blocks() as app:
            gr.Markdown("## Eyeglasses Visual Analyzer")

            with gr.Row():

                # LHS
                with gr.Column(scale=1):
                    csv_input = gr.Textbox(
                        label="Image URLs (one per line / CSV)",
                        placeholder="image URLs here (one per line)...",
                        lines=12
                    )
                    analyze_btn = gr.Button("Analyze Images")
                    all_json_output = gr.HTML()

                # RHS
                with gr.Column(scale=2):
                    results_output = gr.HTML()

            analyze_btn.click(
                fn=self.analyze_bulk,
                inputs=csv_input,
                outputs=[all_json_output, results_output]
            )

        app.launch(server_name="0.0.0.0",server_port=7860,share=False)


if __name__ == "__main__":
    GradioUI().run()
