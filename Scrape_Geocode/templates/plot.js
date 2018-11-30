var collection = '{{list_coll|tojson}}';
var parsed = JSON.parse(collection)
console.log(collection);
console.log(parsed);


var count_skill_dict = {
    'Excel' : 0,
    'SQL': 0,
    'mySQL' : 0,
    'Python': 0,
    'JavaScript': 0,
    'Java': 0,
    'pandas': 0,
    'html': 0,
    'MongoDB': 0,
    'CSS': 0,
    'Leaflet': 0,
    'Numpy': 0,
    'VBA': 0,
    'd3': 0,
    'matplotlib': 0,
    'Tableau': 0,
    'Machine Learning': 0,
    'Bachelors': 0,
    'Masters': 0,
    'PhD':0
    };

parsed.forEach(function(list){
    list.forEach(function(element){
        count_skill_dict[element] += 1;
    });
});

var letters = Object.keys(count_skill_dict);
var counts = Object.values(count_skill_dict);
console.log(letters,counts);

trace1 = {
    x: letters,
    y: counts,
    type: 'bar'
    };


data = [trace1];
Plotly.newPlot('plot',data);