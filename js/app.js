function plistsetup() {
  var selector = d3.select("#sel_div");

  $("#sel_div").prepend("<option value='' selected='selected'>(Select one)</option>");
   d3.json(`/setup`).then((aaa) => {
      aaa.forEach((x) => {
        selector
           .append("option")
           .text(`${x.number} - ${x.president}`)
           .property("value", x.president);
      });
    });
};





function barsearch() {

  var inputElement1 = d3.select("#word-search1");
  var js_search_word = inputElement1.property("value");
  console.log(js_search_word);

  d3.json(`/barchart/${js_search_word}`).then((response) => {
    console.log('got here');
    console.log(response);


      // constructing the svg container
      var svgWidth = 800;
      var svgHeight = 800;

      const marginBar = 80;
      var widthBar = svgWidth - marginBar;
      var heightBar = svgHeight - marginBar;


        const svgBar = d3.select("#bar-chart")
          .append("svg")
          .attr("height",svgHeight)
          .attr("width", svgWidth)
          .style("fill", "rgb(92, 92, 233)");
        const svgContainer = d3.select('#bar-chart');

        const chart = svgBar.append('g')
          .attr('transform', `translate(80, ${marginBar/3.8})`);

        // creating x and y scales
        const xScale = d3.scaleBand()
          .range([0, widthBar])
          .domain(response.map((d) => d.president))
          .padding(0.4)

        const yScale = d3.scaleLinear()
          .range([heightBar,0])
          .domain([0,d3.max(response, d => d.count) + 1])

        // Make horizontal grid lines
        const makeYLines = () => d3.axisLeft()
          .scale(yScale)

        chart.append('g')
          .attr('transform', `translate(0,${heightBar})`)
          .call(d3.axisBottom(xScale))
          .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-45)")

        chart.append('g')
          .call(d3.axisLeft(yScale));

        chart.append('g')
          .attr('class','grid')
          .call(makeYLines()
              .tickSize(-widthBar, 0, 0)
              .tickFormat('')
          )
        const barGroups = chart.selectAll()
          .data(response)
          .enter()
          .append('g')

        // appending the bar chart
        barGroups.append('rect')
          .attr('class', 'bar')
          .attr('x', (d) => xScale(d.president))
          .attr('y', (d) => yScale(d.count))
          .attr('height', (d) => heightBar - yScale(d.count))
          .attr('width', xScale.bandwidth())
          .style("fill", "rgb(92, 92, 233)")

        // appending titles to the page
        svgBar.append('text')
          .attr('class', 'label')
          .attr('x', -(heightBar / 2) - marginBar/2)
          .attr('y', 20)
          .attr('transform', 'rotate(-90)')
          .attr('text-anchor', 'middle')
          .text('Times Word was Used')

        svgBar.append('text')
          .attr('class', 'label')
          .attr('x', widthBar / 2 + marginBar)
          .attr('y', heightBar + (marginBar / 2 ) + 40)
          .attr('text-anchor', 'middle')
          .text('President')

        svgBar.append('text')
          .attr('class', 'title')
          .attr('x', widthBar / 2)
          .attr('y', 20)
          .attr('text-anchor', 'middle')
          .text(`Usage frequency of "${js_search_word}"`)

    }); //end of d3 promise
  }; //end of function








////////////////////////////////




function cloudsearch() {

  var inputElement1 = d3.select("#sel_div");
  var js_search_word = inputElement1.property("value");
  console.log(js_search_word);

  d3.json(`/wordcloud/${js_search_word}`).then((response) => {
    console.log('got here');
    console.log(response);


      var margin = {top: 10, right: 10, bottom: 10, left: 10},
          widthCloud = 900 - margin.left - margin.right,
          height = 800 - margin.top - margin.bottom;

      // append the svg object to the body of the page
      var svg = d3.select("#cloud").append("svg")
          .attr("width", widthCloud + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
        .append("g")
          .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");


      // Constructs a new cloud layout instance. It run an algorithm to find the position of words that suits the requirements
      var layout = d3.layout.cloud()
        .size([widthCloud, height])
        .words(response.map(function(d) { return {text: d.word, size: d.count /5}; }))
        .padding(10)
        .fontSize(function(d) { return d.size; })
        .on("end", draw);
      layout.start();

      // Function to draw each word on the SVG
      function draw(words) {
        svg.append("g")
            .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
            .selectAll("text")
              .data(words)
            .enter().append("text")
              .style("font-size", function(d) { return d.size + "px"; })
              .attr("text-anchor", "middle")
              .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
              })
              .text(function(d) { return d.text; });
        }

  }); //end of d3 promise
}; //end of function






function docsearch() {

  var inputElement1 = d3.select("#word-search2");
  var js_search_term = inputElement1.property("value");
  console.log(js_search_term);

  d3.json(`/readfull/${js_search_term}`).then((response) => {
      console.log('got here');
      console.log(response);

       var tbody = d3.select(".table").select("tbody");
       tbody.html("");
       response.forEach((x) => {

          var row = tbody.append("tr");
          
          Object.entries(x).forEach(([key, value]) => {
            if(key == '_dir' || key == 'filename' || key == 'date' || key == 'president' || key == 'title') {
                var cell = row.append("td");
                cell.text(value);
            }
         });
      });

      $("tr:not(:has(th))").mouseover(function () {
        $(this).addClass("hover");
        });
 
      $("tr:not(:has(th))").mouseleave(function () {
        $(this).removeClass("hover");
        });

    });
};



// jQuery script
$(document).ready(function(){
  $("div.docsList table").delegate('tr', 'click', function() {
      var currentRow=$(this).closest("tr"); // get the current row
      var fp1=currentRow.find("td:eq(0)").text(); // get current row 1st TD value
      var fp2=currentRow.find("td:eq(2)").text();
      var js_filepath = fp1.concat('/', fp2, '.txt')


      $.ajax({
        url : js_filepath,
        dataType: "text",
        success : function (data) {
            //$(".gfg").html(data);
            // var text = d3.select(".gfg").select("p");
            // text.html("")
            document.getElementById("fulltext").innerHTML = ""
            $("#fulltext").append(`${data}`)
        }
      });

    });

  //  $("tr:not(:has(th))").mouseover(function () {
  //      $(this).addClass("hover");
  //      });

  //  $("tr:not(:has(th))").mouseleave(function () {
  //      $(this).removeClass("hover");
  //      });
      
  $( function() {
      $( "#tabs" ).tabs();
      plistsetup();
  } );

});

















