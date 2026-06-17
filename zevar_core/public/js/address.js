frappe.ui.form.on('Address', {
    refresh: function(frm) {
        if (!frm.fields_dict.address_line1) return;
        
        let input_el = frm.fields_dict.address_line1.$input[0];
        if (!input_el || input_el.awesomplete_setup) return;
        
        input_el.awesomplete_setup = true;
        
        // Initialize awesomplete for the address line 1 input
        let awesomplete = new Awesomplete(input_el, {
            minChars: 3,
            maxItems: 8,
            autoFirst: false
        });

        let timeout = null;
        let last_results = [];

        input_el.addEventListener('input', function(e) {
            clearTimeout(timeout);
            let val = e.target.value;
            
            // Only trigger if at least 3 characters are typed
            if (val.length < 3) return;

            timeout = setTimeout(function() {
                // Call OpenStreetMap Nominatim API
                let url = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q=${encodeURIComponent(val)}`;
                
                fetch(url, {
                    headers: {
                        'Accept': 'application/json',
                        'User-Agent': 'Frappe Zevar Core API'
                    }
                })
                .then(res => res.json())
                .then(data => {
                    last_results = data;
                    // Provide the display names as suggestions
                    let list = data.map(item => item.display_name);
                    awesomplete.list = list;
                })
                .catch(err => {
                    console.error("OSM API Error", err);
                });
            }, 600); // 600ms debounce to comply with OSM usage policy
        });

        // When a recommendation is selected
        input_el.addEventListener('awesomplete-selectcomplete', function(e) {
            let selected_name = e.text.value;
            let item = last_results.find(x => x.display_name === selected_name);
            
            if (item && item.address) {
                let address = item.address;
                
                // Construct a cleaner address line 1
                let new_line1 = [];
                if (address.house_number) new_line1.push(address.house_number);
                if (address.road) new_line1.push(address.road);
                if (address.suburb) new_line1.push(address.suburb);
                
                if (new_line1.length > 0) {
                    frm.set_value('address_line1', new_line1.join(', '));
                } else {
                    frm.set_value('address_line1', selected_name.split(',')[0]);
                }

                // Auto-fill other address fields based on the OSM data
                if (address.city || address.town || address.village) {
                    frm.set_value('city', address.city || address.town || address.village);
                }
                if (address.state) {
                    frm.set_value('state', address.state);
                }
                if (address.country) {
                    frm.set_value('country', address.country);
                }
                if (address.postcode) {
                    frm.set_value('pincode', address.postcode);
                }
            }
        });
    }
});
