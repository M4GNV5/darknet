const text_size = 10;

function render_detections(canvas, image_url, objects_promise)
{
	let ctx = canvas.getContext("2d");

	let img_promise = new Promise((resolve, reject) => {
		let img = new Image();
		img.onload = () => resolve(img);
		img.onerror = reject;
		img.src = image_url;
	});

	Promise.all([img_promise, objects_promise])
		.then(([img, objects]) => {
			canvas.width = img.width;
			canvas.height = img.height;
			ctx.drawImage(img, 0, 0);

			objects.forEach(([name, probability, [x, y, w, h]]) => {
				x = x - w / 2;
				y = y - h / 2;

				ctx.strokeStyle = "green";
				ctx.lineWidth = 4;
				ctx.strokeRect(x, y, w, h);

				let text = `${(probability * 100) | 0}% ${name}`;
				let text_width = ctx.measureText(text).width;
				ctx.fillStyle = "green";
				ctx.fillRect(x - 2, y - text_size * 0.75, text_width + 2, text_size * 0.75);

				ctx.fillStyle = "black";
				ctx.font = `${text_size}px Georgia`;
				ctx.fillText(text, x - 1, y);
			});
		});
}
