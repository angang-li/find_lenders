// Fetch lender data from API
const apiURL = "/api_lender_data"

d3.json(apiURL).then(function(data) {

    // console.log(data);
  
    // Render a list of states for selection
    var states = [];
    data.forEach(record => {
        if (!(states.includes(record.State))) {
            states.push(record.State)
        }
    });
    var stateMenu = d3.select('#stateDropdown');
    states.forEach(state => {
        var item = stateMenu.append("option");
        item.text(state.toUpperCase())
    })

    // Render a list of multi-family types for selection
    var mfTypes = [];
    data.forEach(record => {
        if (!(mfTypes.includes(record["Multifamily Subtype"]))) {
            mfTypes.push(record["Multifamily Subtype"])
        }
    });
    var mfMenu = d3.select('#mfDropdown');
    mfTypes.forEach(mf => {
        var item = mfMenu.append("option");
        item.text(mf)
    })
  
  })
