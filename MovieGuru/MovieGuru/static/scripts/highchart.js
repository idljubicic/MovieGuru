$(function () {

    $(document).ready(function () {
        var json = (function () {
            var json = null;
            $.ajax({
                'async': false,
                'global': false,
                'url': '/genres',
                'dataType': "json",
                'success': function (data) {
                    json = data;
                }
            });
            return json;
        })();

        // Build the chart
        Highcharts.chart('container', {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor: null,
                type: 'pie'
            },
            title: {
                text: 'Favourite genres',
                style: { fontFamily: 'sans-serif', lineHeight: '18px', fontSize: '17px', color: 'white' }
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.y}</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true
                }
            },
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: json
            }],
            legend: {
                itemStyle: {
                    color: 'white'
                },
                itemHoverStyle: {
                    color: 'blue'
                },
            }
        });
    });
});