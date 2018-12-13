google.charts.load("current", {packages: ["line", "corechart"]});
let google_charts_loaded = new Promise((resolve) => google.charts.setOnLoadCallback(() => resolve()));

let data;
let data_promise = fetch("data.json")
	.then(res => res.json())
	.then(_data => data = _data);

let draw_btn = document.getElementById("draw-btn");
let from_input = document.getElementById("from");
let to_input = document.getElementById("to");
let chart_el = document.getElementById("chart");

from_input.valueAsNumber = Date.now() - 3 * 24 * 60 * 60 * 1000;
to_input.valueAsNumber = Date.now() - 2.8 * 24 * 60 * 60 * 1000;

Promise.all([data_promise, google_charts_loaded])
	.then(() => drawChart())
	.then(() => draw_btn.disabled = false);

function drawChart()
{
	let table = new google.visualization.DataTable();
	table.addColumn("date", "Date");
	table.addColumn("number", "Car");
	table.addColumn("number", "Truck");
	table.addColumn("number", "Person");

	let min = new Date(from_input.value).getTime();
	let max = new Date(to_input.value).getTime();
	console.log(min, max);
	let rows = [];

	for(let dateStr in data)
	{
		let parts = dateStr.match(/(\d{4})-(\d{2})-(\d{2})-(\d{2}):(\d{2})/iu);
		if(!parts)
			continue;

		let [year, month, day, hour, minute] = parts.slice(1, 6).map(x => parseInt(x));
		let date = new Date(year, month - 1, day, hour, minute);

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
		rows.push([date, values["car"], values["truck"], values["person"]]);
	}

	console.log("Rendering " + rows.length + " rows...");
	rows.sort((a, b) => a[0].getTime() - b[0].getTime());
	table.addRows(rows);

	var chart = new google.charts.Line(chart_el);
	chart.draw(table, {
		chart: {
			title: 'Objects'
		},
		curveType: 'function',
		height: 900,
	});
}
