const socket = io();
const ctx = document.getElementById('myChart').getContext('2d');

const myGraphic = new Chart(ctx, {
	type: 'bar',
	data: {},
	options: {
		scales: {
			y: {
				beginAtZero: true,
			},
		},
	},
});

socket.on('connection', (data) => {
	console.log(data.message);

	myGraphic.data.labels = Object.keys(data.topTen);

	console.log(myGraphic.data.datasets.length);
	if (myGraphic.data.datasets.length == 0) {
		myGraphic.data.datasets.push({
			label: '10 sitios mas visitados',
			data: Object.values(data.topTen),
			borderWidth: 1,
		});
	} else {
		myGraphic.clear();
		myGraphic.data.datasets[0].data = Object.values(data.topTen);
	}

	myGraphic.update();
});

socket.on('update_graphic', (data) => {
	myGraphic.data.datasets[0].data = Object.values(data.topTen);
	myGraphic.data.labels = Object.keys(data.topTen);
	myGraphic.update();
});
