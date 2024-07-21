const rangeSlider_min = 0;
const rangeSlider_max = 100;
var minSliderValue = 0;
var maxSliderValue = 100;
var currentMinSliderValue = 0;
var currentMaxSliderValue = 100;

var slider = document.getElementById('slider');
var config = {
	start: [minSliderValue, maxSliderValue],
	connect: true,
	range: {
		'min': minSliderValue,
		'max': maxSliderValue
	},
	tooltips: [
		{
			to: function (value) {
				if (graph_data_cache === null) {
					return value;
				}
				return graph_data_cache['data_hora'][parseInt(value)];
			}
		},
		{
			to: function (value) {
				if (graph_data_cache === null) {
					return value;
				}
				console.log(parseInt(value))
				return graph_data_cache['data_hora'][parseInt(value)];
			}
		}
	]
}

noUiSlider.create(slider, config);

slider.noUiSlider.on('update', function (value) {
	currentMinSliderValue = parseInt(value[0]);
	currentMaxSliderValue = parseInt(value[1]);
});

function UpdateSlider() {
	config.range['max'] = maxSliderValue;
	config.start[0] = currentMinSliderValue;
	config.start[1] = (currentMaxSliderValue == (maxSliderValue - 1)) ? maxSliderValue : currentMaxSliderValue;
	slider.noUiSlider.updateOptions(config);
}