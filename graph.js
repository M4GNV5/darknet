let draw_btn = document.getElementById("draw-btn");
let from_input = document.getElementById("from");
let to_input = document.getElementById("to");
let chart_el = document.getElementById("chart");
let canvas_el = document.getElementById("canvas");

let data;
let table;
let chart;

from_input.valueAsNumber = Date.now() - 7 * 24 * 60 * 60 * 1000;
to_input.valueAsNumber = Date.now();

google.charts.load("current", {packages: ["line", "corechart"]});
google.charts.setOnLoadCallback(() => fetch_data());

function pad(val, len, c)
{
	c = c || ' ';
	val = val.toString();
	return Array(len - val.length).fill(c).join('') + val;
}

function fetch_data()
{
	draw_btn.disabled = true;
	chart_el.innerHTML = "Loading...";

	let min = new Date(from_input.value).getTime();
	let max = new Date(to_input.value).getTime();

	let data_fetches = [];
	for(let curr = min; curr < max; curr += 24 * 60 * 60 * 1000)
	{
		let date = new Date(curr);
		date = pad(date.getFullYear(), 4, '0') + "-" + pad(date.getMonth() + 1, 2, '0') + "-" + pad(date.getDate(), 2, '0');
		console.log(curr, new Date(curr), date);
		data_fetches.push(fetch("json/hdb-" + date + ".json")
			.then(res => res.json())
			.catch(res => ({}))
		);
	}

	Promise.all(data_fetches)
		.then(data => data.reduce((x, y) => Object.assign(x, y), {}))
		.then(data => draw_chart(data, min, max));
}

function draw_chart(_data, min, max)
{
	data = _data;

	table = new google.visualization.DataTable();
	table.addColumn("date", "Date");
	table.addColumn("number", "Car");
	table.addColumn("number", "Truck");
	table.addColumn("number", "Person");

	let rows = [];

	for(let dateStr in data)
	{
		let parts = dateStr.match(/hdb_(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2}):(\d{2})/iu);
		if(!parts)
			continue;

		let [year, month, day, hour, minute, seconds] = parts.slice(1, 7).map(x => parseInt(x));
		let date = new Date(year, month - 1, day, hour, minute, seconds);

		if(date.getTime() < min || date.getTime() > max)
			continue;

		let values = {};
		for(let item of data[dateStr])
		{
			let [name, confidence, ] = item;
			if(confidence > 0.5)
			{
				values[name] = values[name] || 0;
				values[name]++;
			}
		}
		rows.push([
			date,
			values["car"] || 0,
			values["truck"] || 0,
			values["person"] || 0,
		]);
	}

	rows.sort((a, b) => a[0].getTime() - b[0].getTime());
	console.dir(rows);

	let rows2 = [];
	let combine = Math.floor(rows.length / 500);
	for(let i = 0; i < rows.length; )
	{
		let count = 1;
		let val = rows[i];
		i++;

		let stop = Math.min(rows.length, i + combine);
		for( ; i < stop; i++)
		{
			for(let k = 1; k < rows[i].length; k++)
				val[k] += rows[i][k];

			count++;
		}

		for(let k = 1; k < val.length; k++)
			val[k] /= count;

		rows2.push(val);
	}

	rows = rows2;

	console.log("Rendering " + rows.length + " rows...");
	table.addRows(rows);

	chart = new google.charts.Line(chart_el);
	chart.draw(table, {
		chart: {
			title: 'Objects'
		},
		curveType: 'function',
		height: 700,
	});

	google.visualization.events.addListener(chart, 'select', show_details);

	draw_btn.disabled = false;
}

function show_details()
{
	let selection = chart.getSelection()[0];
	if(!selection || !selection.row)
		return;

	let date = table.getValue(selection.row, 0);
	date = new Date(date.getTime() - date.getTimezoneOffset() * 60 * 1000);

	let name = "hdb_" + date.toISOString().substr(0, 19).replace("T", "-");
	let dat = data[name];

	if(!dat)
		return;

	render_detections(canvas_el, `img_raw/${name}.jpg`, Promise.resolve(dat));
}
