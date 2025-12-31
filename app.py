from flask import Flask, jsonify, render_template
import docker

app = Flask(__name__)
client = docker.from_env()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/containers")
def containers():
    running = client.containers.list()
    data = []
    for c in running:
        data.append({
            "id": c.short_id,
            "name": c.name,
            "image": c.image.tags[0] if c.image.tags else "None",
            "status": c.status
        })
    return jsonify({
        "total_running": len(running),
        "containers": data
    })

@app.route("/images")
def images():
    all_images = client.images.list()
    data = []
    for img in all_images:
        data.append({
            "id": img.short_id.replace("sha256:", ""),
            "tags": img.tags if img.tags else ["<none>"],
            "size": f"{img.attrs['Size'] / (1024*1024):.2f} MB",
            "created": img.attrs['Created']
        })
    return jsonify({
        "total_images": len(all_images),
        "images": data
    })

@app.route("/stats")
def stats():
    running_containers = client.containers.list()
    all_containers = client.containers.list(all=True)
    all_images = client.images.list()
    
    stopped = len([c for c in all_containers if c.status != "running"])
    
    return jsonify({
        "running_containers": len(running_containers),
        "stopped_containers": stopped,
        "total_images": len(all_images),
        "total_containers": len(all_containers)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
