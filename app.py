
import gradio as gr
import torch
from diffusers import DiffusionPipeline

# Replace with your actual repo after upload, e.g. "username/my-text2video-model"
HF_MODEL_ID = gr.State("username/my-text2video-model")

def load_pipe(model_id):
    pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, variant="fp16")
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return pipe

_cached = {"pipe": None, "model_id": None}

def generate(prompt, num_frames, guidance_scale, steps, model_id):
    global _cached
    if _cached["pipe"] is None or _cached["model_id"] != model_id:
        _cached["pipe"] = load_pipe(model_id)
        _cached["model_id"] = model_id

    pipe = _cached["pipe"]
    out = pipe(prompt, num_frames=int(num_frames), guidance_scale=float(guidance_scale), num_inference_steps=int(steps))
    # Gradio supports returning a list of frames; many Spaces also expect a video file path.
    # Here we return frames; you can also write frames to mp4 if needed.
    return out.frames

with gr.Blocks() as demo:
    gr.Markdown("# 🎬 Text → Video Demo")
    with gr.Row():
        prompt = gr.Textbox(label="Prompt", placeholder="A white cat dancing in space, cinematic, 4k")
    with gr.Row():
        num_frames = gr.Slider(8, 32, value=16, step=1, label="Frames")
        guidance = gr.Slider(0.0, 15.0, value=7.5, step=0.5, label="Guidance Scale")
        steps = gr.Slider(10, 50, value=25, step=1, label="Inference Steps")
    model_id = gr.Textbox(label="HF Model ID", value="username/my-text2video-model")
    btn = gr.Button("Generate")
    gallery = gr.Gallery(label="Frames").style(grid=4, height=400)

    btn.click(fn=generate, inputs=[prompt, num_frames, guidance, steps, model_id], outputs=gallery)

if __name__ == "__main__":
    demo.launch()
