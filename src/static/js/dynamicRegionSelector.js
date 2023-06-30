let ancestors = [];
let selected_regions = [];
let selected_regions_json = [];
let region_long_name = [];
let adv_level = ["Dep", "Com", "Arr", "vlg"]

$("#id_administrative_level").val(null).trigger('change.select2');

function toggleAddButton() {
    if ($("select.region:first").val()) {
        $('#add').removeClass('disabled');
    } else {
        $('#add').addClass('disabled');
    }
}

function toggleSubmitButton() {
    if (selected_regions.length > 0) {
        $('#submit').prop('disabled', false);
    } else {
        $('#submit').prop('disabled', true);
        toggleAddButton();
    }
}

function changeRegionTrigger(url, placeholder) {
    $(document).on("change", ".region", function () {
        loadNextLevelRegions($(this), url, placeholder);
    });
}

function addSelectedRegion(selected_region, regions, s_indice){
    // console.log("selecting: ", selected_region);
    let administrative_id = selected_region.val();

    // only add unique administrative level
    if (administrative_id && selected_regions.indexOf(administrative_id) === -1){
        selected_regions.push(administrative_id);
        let region_name = $('#' + selected_region[0].id + ' option:selected').text();
        // if (region_name && region_long_name.indexOf(region_name) === -1){
        //     region_long_name.push(region_name);
        // }
        
        
        // for (let i=1; i< regions.length; i++){
        //     previous_region = regions.eq(regions.index(selected_region) - i);
        //     previous_region_name = $('#' + previous_region[0].id + ' option:selected').text() + " (" + adv_level[s_indice+i] + ")";
        //     if (previous_region_name && region_long_name.indexOf(previous_region_name) === -1){
        //         region_long_name.push(previous_region_name);
        //     }
        // }
        let selected_region_json = {
            "name": region_name,
            "id": administrative_id
        };
        selected_regions_json.push(selected_region_json);
        $("#id_administrative_levels").val(JSON.stringify(selected_regions_json));
        // console.log("regions json", selected_regions_json)
        $(this).addClass('disabled');
        $('#' + administrative_id).prop('disabled', true);
        // let rregion_long_name = $("select.region").map(function () {
        //     return this.options[this.selectedIndex].text;
        // }).get().reverse().join(", ");
        // let rregion_long_name = region_long_name.join(", ");
        // rregion_long_name.slice(0, rregion_long_name.indexOf(region_name) + region_name.length)
        let region_html = "<a class='tag mt-2' >" +
            "<i value='" + administrative_id + "' class='fa fa-remove mr-2 link remove-region' title='Remove'></i>" +
            region_name + " (" + adv_level[s_indice] + ")" + "</a>";
        $("#selected_regions").append(region_html);
        region_long_name = []
    }
    // else {
    //     alert("Niveau administratif déjà ajouter")
    // }
}

$(document).on("click", "#add", function () {
    // let selected_region = $("select.region:last");
    // //// if last region not selected,
    // //// add previous adminitrative level
    // if(!selected_region.val()){
    //     selected_region = $("select.region").eq(-2)
    // }
    // addSelectedRegion(selected_region)
    var regions = $("select.region");
    var total_regions = regions.length;
    for (var s_indice = 0; s_indice < total_regions; s_indice++) {
        addSelectedRegion($(regions.eq(s_indice)), regions, s_indice)
    }
    // regions.each(function() {
    //     addSelectedRegion($(this), regions);
    // });
    toggleSubmitButton();
});

$(document).on("click", ".remove-region", function () {
    let administrative_id = $(this).attr('value');
    $(this).parent().remove();
    $('#' + administrative_id).prop('disabled', false);
    selected_regions = $.grep(selected_regions, function (e) {
        return e !== administrative_id;
    });
    selected_regions_json = $.grep(selected_regions_json, function (e) {
        return e.id !== administrative_id;
    });
    $("#id_administrative_levels").val(JSON.stringify(selected_regions_json));
    toggleSubmitButton();
});

function loadNextLevelRegions(current_level, url, placeholder) {
    let current_level_val = current_level.val();
    //console.log('current_level_val para cargar proximo selector: ' + current_level_val);
    if (current_level_val !== '') {
        let select_region = $(".region");
        select_region.attr('disabled', true);
        $.ajax({
            type: 'GET',
            url: url,
            data: {
                parent_id: current_level_val,
            },
            success: function (data) {
                if (data.length > 0) {
                    let id_select = 'id_' + slugify(data[0].administrative_level, '_');
                    let label = data[0].administrative_level.toUpperCase();
                    let child;
                    let new_input = document.createElement('div');
                    new_input.className = 'form-group row dynamic-select';

                    let label_element = document.createElement('label');
                    label_element.className = 'col-md-3 col-form-label';
                    label_element.setAttribute('for', id_select);
                    label_element.innerHTML = label;
                    new_input.appendChild(label_element);

                    let div_element = document.createElement('div');
                    div_element.className = 'col-md-9';

                    let select_element = document.createElement('select');
                    select_element.className = 'form-control region';
                    select_element.setAttribute("required", "");
                    select_element.setAttribute('id', id_select);
                    div_element.appendChild(select_element);

                    new_input.appendChild(div_element);

                    current_level.parent().parent().after(new_input);
                    child = current_level.closest('.form-group').next().find('.region');
                    child.select2({
                        allowClear: true,
                        placeholder: placeholder,
                    });
                    $(child).next().find('b[role="presentation"]').hide();
                    $(child).next().find('.select2-selection__arrow').append(
                        '<i class="fas fa-chevron-circle-down text-primary" style="margin-top:12px;"></i>');

                    let options = '<option value></option>';
                    $.each(data, function (index, value) {
                        let administrative_id = value.administrative_id;
                        let option = '<option id="' + administrative_id + '" value="' + administrative_id + '"';
                        if (selected_regions.includes(administrative_id)) {
                            option += ' disabled ';
                        }
                        if (ancestors.includes(administrative_id)) {
                            option += ' selected="selected">';
                            ancestors = ancestors.filter(function (ancestor) {
                                return ancestor !== administrative_id;
                            });
                        } else {
                            option += '>';
                        }
                        option += value.name + '</option>';
                        options += option

                    });
                    child.html(options);
                    child.trigger('change');
                    let child_val = child.val();
                    if (child_val !== '') {
                        child.val(child_val)
                    }
                }
            },
            error: function (data) {
                alert(error_server_message + "Error " + data.status);
            }
        }).done(function () {
                if (ancestors.length <= 1) {
                    select_region.attr('disabled', false);
                }
                toggleAddButton();
            }
        );
    } else {
        let next_selects = current_level.closest('.form-group').nextAll('.dynamic-select');
        $.each(next_selects, function (index, select) {
            select.remove();
        });
        toggleAddButton();
    }
}

function loadRegionSelectors(url) {
    let administrative_levels = $("#id_administrative_levels").val();
    $.ajax({
        type: 'GET',
        url: url,
        data: {
            administrative_id: administrative_levels,
        },
        success: function (data) {
            if (data.length > 0) {
                data = data.slice(1);
                data.push(administrative_levels);
                ancestors = data;
                loadNextLevelRegions($("select.region:last"), get_choices_url, choice_placeholder);
            }
        },
        error: function (data) {
            alert(error_server_message + "Error " + data.status);
        }
    });
}
