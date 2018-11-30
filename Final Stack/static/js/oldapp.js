window.smoothScroll = function(target) {
    var scrollContainer = target;
    do { //find scroll container
        scrollContainer = scrollContainer.parentNode;
        if (!scrollContainer) return;
        scrollContainer.scrollTop += 1;
    } while (scrollContainer.scrollTop == 0);

    var targetY = 0;
    do { //find the top of target relatively to the container
        if (target == scrollContainer) break;
        targetY += target.offsetTop;
    } while (target = target.offsetParent);

    scroll = function(c, a, b, i) {
        i++; if (i > 30) return;
        c.scrollTop = a + (b - a) / 30 * i;
        setTimeout(function(){ scroll(c, a, b, i); }, 20);
    }
    // start scrolling
    scroll(scrollContainer, scrollContainer.scrollTop, targetY, 0);
}
// jobs.forEach(function(job) {
//   console.log(job);
// })

// d3.select("#jobs").selectAll("div")
//   .data(jobs)
//   .enter()
//   .append("div")
//   .attr("class", "card")
//   .style("width", "18rem")
//   .append("div")
//   .attr("class", "card-header")
//   .text(function(d) {
//     return d.properties['job title'];
//   })
//   .append("div")
//   .attr("class", "card-body")
//   .text(function(d) {
//     return d.properties.company;
//   });



// Define streetmap and darkmap layers
var streetmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 18,
  id: "mapbox.streets",
  accessToken: API_KEY
});

var darkmap = L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
  attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
  maxZoom: 18,
  id: "mapbox.dark",
  accessToken: API_KEY
});

// Define a baseMaps object to hold our base layers
var baseMaps = {
  "Street Map": streetmap,
  "Dark Map": darkmap
};

// Create our map, giving it the streetmap and all jobs layers to display on load
var myMap = L.map("map", {
  center: [
    37.7749295,-122.4194155
  ],
  zoom: 6,
  layers: [streetmap]
});

// creates outline of California using Chloropleth plugin
var caData = statesData.features.filter(d => d.properties.name === 'California');
L.geoJson(caData, {style: {color: 'black'}}).addTo(myMap);

var layerscontrol = L.control.layers(baseMaps).addTo(myMap);

var overlayMaps = {};
var skills_dict;

function generateMap(jobs) {

  // Dictionary that will hold list of jobs pertaining to that skill
  skills_dict = {
    'Excel': [],
    'SQL': [],
    'mySQL': [],
    'Python': [],
    'JavaScript': [],
    'Java': [],
    'pandas': [],
    'html': [],
    'MongoDB': [],
    'CSS': [],
    'Leaflet': [],
    'Numpy': [],
    'VBA': [],
    'd3': [],
    'matplotlib': [],
    'Plotly': [],
    'Tableau': [],
    'Machine Learning': [],
    'R': [],
    'Bachelors': [],
    'Masters': [],
    'PhD': []
  }

  // Delete all layers to generate new map
  layerscontrol.remove();
  if (counter > 1) {    
    for (var key in overlayMaps) {
      console.log(overlayMaps[key])
      myMap.removeLayer(overlayMaps[key]);
    }
  }

  // for each job, look if each of its skills has a corresponding key in skills_dict
  // if it does, append that job to that key's list
  for(var i = 0; i < jobs.length; i++) {
    var current_skills = jobs[i].properties.Skills_List;

    current_skills.forEach(function(skill) {
      if (skill in skills_dict) {
        skills_dict[skill].push(jobs[i]);
      }
    });
  }

  // Define a function we want to run once for each feature in the features array
  // Give each feature a popup which includes job title, company name and relevant skills
  function onEachFeature(feature, layer) {
    layer.bindPopup("<h3><a href='" + feature.properties.Job_Posting_URL + "'>"+ feature.properties.Job_Title +
      "</a></h3><p>Company: " + feature.properties.Company+ "</p><p>Source: " + feature.properties.Website + "</p><hr><p>Skills: " 
      + feature.properties.Skills_List + "</p>");
  }

  // Create custom marker for each job
  // Documentation: https://github.com/coryasilva/Leaflet.ExtraMarkers
  var redMarker = L.ExtraMarkers.icon({
      icon: 'fa-database',
      markerColor: 'orange-dark',
      shape: 'square',
      prefix: 'fa'
    });

  function pointToLayer(feature, latlng) {
    return L.marker(latlng, {icon: redMarker});
  }

  // Create a geoJSON layer that contains all jobs
  jobLayer = L.geoJSON(jobs, {
    pointToLayer: pointToLayer,
    onEachFeature: onEachFeature
  });

  overlayMaps["All Jobs"] = jobLayer;

  // Create a geoJSON layer for each language/skill
  for (var key in skills_dict) {
    // Don't create a layer for the skills that have no jobs (i.e. the keys that have an associated empty array value)
    if (skills_dict[key].length !== 0) {
      overlayMaps[`${key} Jobs`] = L.geoJson(skills_dict[key], {
        pointToLayer: pointToLayer,
        onEachFeature: onEachFeature
      });
    }  
  }
  
  // Create a layer control
  // Pass in our baseMaps and overlayMaps
  // Add the layer control to the map
  layerscontrol = L.control.layers(baseMaps, overlayMaps, {
    collapsed: false
  }).addTo(myMap);
}

var counter = 0;
var url;
var currentJob;
var button = d3.selectAll(".job-option");

// generate a map based on what button was clicked
button.on("click", function() {

  counter = counter + 1; 
  // reset button's style
  button.style("opacity", 1);
  selectedbtn = d3.select(this);

  selectedbtn.style("opacity", 0.5);

  // if user reselects same button, simply do nothing (do not regenerate map)
  if (currentJob === selectedbtn.text()) {
    console.log("We're already here!")
    return;
  // otherwise, set url to endpoint based on what button was selected
  } else {
    currentJob = selectedbtn.text()
    if (currentJob === 'Data Analyst') {
      url = '/leaflet-analyst';
      console.log(url);
    } else if (currentJob === 'Data Scientist') {
      url = '/leaflet-scientist';
    }
    d3.json(url, function(raw_job_data) {
      generateMap(raw_job_data);
    })
  }
  
  
})

var graph_url = '/';
d3.json(graph_url, function(list_coll, list_coll2) {
  var collection = list_coll;
  console.log(collection);
  // var collection2 = list_coll2;

  // var count_skill_dict = {
  //     'Excel' : 0,
  //     'SQL': 0,
  //     'mySQL' : 0,
  //     'Python': 0,
  //     'JavaScript': 0,
  //     'Java': 0,
  //     'pandas': 0,
  //     'html': 0,
  //     'MongoDB': 0,
  //     'CSS': 0,
  //     'Leaflet': 0,
  //     'Numpy': 0,
  //     'VBA': 0,
  //     'd3': 0,
  //     'matplotlib': 0,
  //     'Tableau': 0,
  //     'Machine Learning': 0,
  //     'Bachelors': 0,
  //     'Masters': 0,
  //     'R':0,
  //     'PhD':0,
  //     'Plotly':0
  //     };
  // var count_skill_dict2 = {
  //     'Excel' : 0,
  //     'SQL': 0,
  //     'mySQL' : 0,
  //     'Python': 0,
  //     'JavaScript': 0,
  //     'Java': 0,
  //     'pandas': 0,
  //     'html': 0,
  //     'MongoDB': 0,
  //     'CSS': 0,
  //     'Leaflet': 0,
  //     'Numpy': 0,
  //     'VBA': 0,
  //     'd3': 0,
  //     'matplotlib': 0,
  //     'Tableau': 0,
  //     'Machine Learning': 0,
  //     'R':0,
  //     'Bachelors': 0,
  //     'Masters': 0,
  //     'PhD':0,
  //     'Plotly':0
  //     };

  // collection.forEach(function(list){
  //     list.forEach(function(element){
  //         count_skill_dict[element] += 1;
  //     });
  // });
  // collection2.forEach(function(list2){
  //     list2.forEach(function(element2){
  //         count_skill_dict2[element2] += 1;
  //     });
  // });
  // var letters = Object.keys(count_skill_dict);
  // var counts = Object.values(count_skill_dict);
  // console.log(letters,counts);
  // var letters2 = Object.keys(count_skill_dict2);
  // var counts2 = Object.values(count_skill_dict2);
  // console.log(letters2,counts2);
  // var trace1 = {
  //     x: letters,
  //     y: counts,
  //     type: 'bar',
  //     name: "Data Analyst Skills"
  //     };
  // var trace2 = {
  //     x: letters2,
  //     y: counts2,
  //     type: 'bar',
  //     name: "Data Scientist Skills"
  //     };
  // var layout = {
  //     barmode: 'group'};
  // var data = [trace1, trace2];
  // Plotly.newPlot('plot',data, layout);
});



