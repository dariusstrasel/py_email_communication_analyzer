var tasks = [
{"startDate":new Date("Sun Dec 09 00:00:45 EST 2012"),"endDate":new Date("Sun Dec 09 02:36:45 EST 2012"),"taskName":"E Job","status":"RUNNING"},
{"startDate":new Date("Sun Dec 09 08:49:53 EST 2012"),"endDate":new Date("Sun Dec 09 06:34:04 EST 2012"),"taskName":"D Job","status":"RUNNING"},
{"startDate":new Date("Sun Dec 09 03:27:35 EST 2012"),"endDate":new Date("Sun Dec 09 03:58:43 EST 2012"),"taskName":"P Job","status":"SUCCEEDED"},
{"startDate":new Date("Sun Dec 09 03:27:35 EST 2012"),"endDate":new Date("Sun Dec 09 03:58:43 EST 2012"),"taskName":"N Job","status":"KILLED"}
];

// var svg2 = d3.select("body").append("svg")
// .attr("width", 960)
// .attr("height", 100)

// svg2.append("text")
//   .text(d3.timeDay.offset(getEndDate(), -7))
//   .attr("y", 50)

var taskStatus = {
    "SUCCEEDED" : "bar",
    "FAILED" : "bar-failed",
    "RUNNING" : "bar-running",
    "KILLED" : "bar-killed"
};

var taskNames = [ "D Job", "P Job", "E Job", "A Job", "N Job" ];

tasks.sort(function(a, b) {
    return a.endDate - b.endDate;
});
var maxDate = tasks[tasks.length - 1].endDate;
tasks.sort(function(a, b) {
    return a.startDate - b.startDate;
});
var minDate = tasks[0].startDate;

var format = "%H:%M";
var timeDomainString = "1day";

var gantt = d3.gantt().height(window.innerHeight).width(window.innerWidth).taskTypes(taskNames).taskStatus(taskStatus).tickFormat(format);

window.addEventListener('resize', resizeSVG);

function resizeSVG (){
    var chart_em = $('svg.chart')[0];
    chart_em.clientHeight = window.innerHeight;
    chart_em.clientWidth = window.innerWidth;
    var chart_child = $('g.gantt-chart');
    chart_child.attr('width', window.innerWidth);
    chart_child.attr('height', window.innerHeight);
}

// gantt.timeDomainMode("fixed");
changeTimeDomain(timeDomainString);
gantt(tasks);

function changeTimeDomain(timeDomainString) {
    this.timeDomainString = timeDomainString;
    switch (timeDomainString) {
    case "1hr":
      format = "%H:%M:%S";
      gantt.timeDomain([ d3.timeHour.offset(getEndDate(), -1), getEndDate() ]);
      break;
    case "3hr":
      format = "%H:%M";
      gantt.timeDomain([ d3.timeHour.offset(getEndDate(), -3), getEndDate() ]);
      break;

    case "6hr":
      format = "%H:%M";
      gantt.timeDomain([ d3.timeHour.offset(getEndDate(), -6), getEndDate() ]);
      break;

    case "1day":
			format = "%H:%M";
			gantt.timeDomain([ d3.timeDay.offset(getEndDate(), -1), getEndDate() ]);
			break;

    case "1week":
      format = "%a %H:%M";
      gantt.timeDomain([ d3.timeDay.offset(getEndDate(), -7), getEndDate() ]);
      break;
    default:
	format = "%H:%M"

    }
    gantt.tickFormat(format);
    gantt.redraw(tasks);
}

function getEndDate() {
    var lastEndDate = Date.now();
    if (tasks.length > 0) {
			lastEndDate = tasks[tasks.length - 1].endDate;
    }
    return lastEndDate;
}

function addTask() {

    var lastEndDate = getEndDate();
    var taskStatusKeys = Object.keys(taskStatus);
    var taskStatusName = taskStatusKeys[Math.floor(Math.random() * taskStatusKeys.length)];
    var taskName = taskNames[Math.floor(Math.random() * taskNames.length)];

    tasks.push({
	"startDate" : d3.timeHour.offset(lastEndDate, Math.ceil(1 * Math.random())),
	"endDate" : d3.timeHour.offset(lastEndDate, (Math.ceil(Math.random() * 3)) + 1),
	"taskName" : taskName,
	"status" : taskStatusName
    });

    changeTimeDomain(timeDomainString);
    gantt.redraw(tasks);
};

function removeTask() {
    tasks.pop();
    changeTimeDomain(timeDomainString);
    gantt.redraw(tasks);
};