$(document).ready(function() {
    const colors = ['#FFDDC1', '#C1FFD7', '#FFD1C1', '#C1D4FF'];

    function showMessage(type, message) {
        let alertDiv = type === 'success' ? $('#success-message') : $('#warning-message');
        alertDiv.text(message).show();
        setTimeout(() => {
            alertDiv.hide();
        }, 3000);
    }

    function showSpinner() {
        $('#loading-spinner').show();
    }

    function hideSpinner() {
        $('#loading-spinner').hide();
    }

    function fetchEntities(device, callback) {
        $.get(`/entities/${device}`, function(data) {
            callback(data.entities);
        });
    }

    function fetchDevices(callback) {
        $.get('/devices_list', function(data) {
            if (data.devices) {
                data.devices.sort(); // Sort the device list alphabetically
                callback(data.devices);
            } else {
                showMessage('warning', 'No devices found. Please fetch devices first.');
            }
        }).fail(function(response) {
            showMessage('warning', response.responseJSON.message);
        });
    }

    function createDropdown(options, selectedOption) {
        let select = $('<select class="form-control"></select>');
        let defaultOption = $('<option></option>').val('').text('Select an option');
        select.append(defaultOption);
        options.forEach(option => {
            let optionElement = $('<option></option>').val(option).text(option);
            if (option === selectedOption) {
                optionElement.attr('selected', 'selected');
            }
            select.append(optionElement);
        });
        select.attr('title', selectedOption); // Add title for hover tooltip
        return select;
    }

    function canCheckThreeWay(row) {
        let sourceDevice = row.find('td:eq(0) select').val();
        let sourceEntity = row.find('td:eq(1) select').val();
        let targetDevice = row.find('td:eq(3) select').val();
        let targetEntity = row.find('td:eq(4) select').val();
        return sourceDevice && sourceEntity && targetDevice && targetEntity;
    }

    function isDuplicateRow(sourceDevice, sourceEntity, targetDevice, targetEntity) {
        let isDuplicate = false;
        $('#mappings-table tbody tr').each(function() {
            let existingSourceDevice = $(this).find('td:eq(0) select').val();
            let existingSourceEntity = $(this).find('td:eq(1) select').val();
            let existingTargetDevice = $(this).find('td:eq(3) select').val();
            let existingTargetEntity = $(this).find('td:eq(4) select').val();
            if (existingSourceDevice === sourceDevice && existingSourceEntity === sourceEntity &&
                existingTargetDevice === targetDevice && existingTargetEntity === targetEntity) {
                isDuplicate = true;
                return false; // break the loop
            }
        });
        return isDuplicate;
    }

    function isSameSourceAndTarget(row) {
        let sourceDevice = row.find('td:eq(0) select').val();
        let sourceEntity = row.find('td:eq(1) select').val();
        let targetDevice = row.find('td:eq(3) select').val();
        let targetEntity = row.find('td:eq(4) select').val();
        return sourceDevice === targetDevice && sourceEntity === targetEntity;
    }

    function highlightDuplicateRows() {
        let rowGroups = {};
        $('#mappings-table tbody tr').each(function() {
            let sourceDevice = $(this).find('td:eq(0) select').val();
            let sourceEntity = $(this).find('td:eq(1) select').val();
            let targetDevice = $(this).find('td:eq(3) select').val();
            let targetEntity = $(this).find('td:eq(4) select').val();
            let key = `${sourceDevice}-${sourceEntity}-${targetDevice}-${targetEntity}`;
            if (!rowGroups[key]) {
                rowGroups[key] = [];
            }
            rowGroups[key].push($(this));
        });

        let colorIndex = 0;
        for (let key in rowGroups) {
            if (rowGroups[key].length > 1) {
                rowGroups[key].forEach(row => {
                    row.css('background-color', colors[colorIndex % colors.length]);
                    row.find('.duplicate-label').remove();
                    row.find('.delete-row-btn').before('<span class="duplicate-label badge badge-danger">Duplicate</span>');
                });
                colorIndex++;
            } else {
                rowGroups[key].forEach(row => {
                    row.css('background-color', '');
                    row.find('.duplicate-label').remove();
                });
            }
        }
    }

    function addMappingRow(mapping, isThreeWay = false) {
        let tbody = $('#mappings-table tbody');
        let tr = $('<tr></tr>');

        let sourceDeviceSelect = $('<td></td>');
        let sourceEntitySelect = $('<td></td>');
        let targetDeviceSelect = $('<td></td>');
        let targetEntitySelect = $('<td></td>');

        tr.append(sourceDeviceSelect);
        tr.append(sourceEntitySelect);
        tr.append('<td class="arrow">→</td>');
        tr.append(targetDeviceSelect);
        tr.append(targetEntitySelect);
        tr.append(`<td><input type="checkbox" class="three-way" ${mapping && mapping.three_way ? 'checked' : ''} ${isThreeWay ? 'disabled' : ''}></td>`);
        tr.append('<td><button class="btn btn-danger btn-sm delete-row-btn">Delete</button></td>');

        if (isThreeWay) {
            tr.addClass('three-way-row');
        }

        tbody.append(tr);

        fetchDevices(function(devices) {
            let sourceDeviceDropdown = createDropdown(devices, mapping ? mapping.source_device : '');
            let targetDeviceDropdown = createDropdown(devices, mapping ? mapping.target_device : '');

            sourceDeviceSelect.append(sourceDeviceDropdown);
            targetDeviceSelect.append(targetDeviceDropdown);

            function updateEntitySelect(deviceDropdown, entitySelect, selectedEntity) {
                let device = deviceDropdown.val();
                fetchEntities(device, function(entities) {
                    entitySelect.empty().append(createDropdown(entities, selectedEntity));
                    highlightDuplicateRows(); // Highlight rows whenever entity dropdown is updated
                });
            }

            sourceDeviceDropdown.change(function() {
                updateEntitySelect(sourceDeviceDropdown, sourceEntitySelect, mapping ? mapping.source_entity_id : '');
            }).trigger('change');

            targetDeviceDropdown.change(function() {
                updateEntitySelect(targetDeviceDropdown, targetEntitySelect, mapping ? mapping.target_entity_id : '');
            }).trigger('change');

            tr.find('.three-way').change(function() {
                if (this.checked) {
                    if (!canCheckThreeWay(tr)) {
                        this.checked = false;
                        showMessage('warning', 'Please fill all fields before enabling three-way.');
                        return;
                    }
                    let sourceDevice = tr.find('td:eq(0) select').val();
                    let sourceEntity = tr.find('td:eq(1) select').val();
                    let targetDevice = tr.find('td:eq(3) select').val();
                    let targetEntity = tr.find('td:eq(4) select').val();

                    if (isDuplicateRow(targetDevice, targetEntity, sourceDevice, sourceEntity)) {
                        this.checked = false;
                        showMessage('warning', 'Duplicate row detected.');
                        return;
                    }

                    let reverseMapping = {
                        source_device: targetDevice,
                        source_entity_id: targetEntity,
                        target_device: sourceDevice,
                        target_entity_id: sourceEntity,
                        three_way: true
                    };
                    addMappingRow(reverseMapping, true);
                    highlightDuplicateRows();
                } else {
                    let sourceDevice = tr.find('td:eq(0) select').val();
                    let sourceEntity = tr.find('td:eq(1) select').val();
                    let targetDevice = tr.find('td:eq(3) select').val();
                    let targetEntity = tr.find('td:eq(4) select').val();
                    tbody.find('.three-way-row').each(function() {
                        if ($(this).find('td:eq(0) select').val() === targetDevice &&
                            $(this).find('td:eq(1) select').val() === targetEntity &&
                            $(this).find('td:eq(3) select').val() === sourceDevice &&
                            $(this).find('td:eq(4) select').val() === sourceEntity) {
                            $(this).remove();
                        }
                    });
                    highlightDuplicateRows();
                }
            });

            tr.find('.delete-row-btn').click(function() {
                let sourceDevice = tr.find('td:eq(0) select').val();
                let sourceEntity = tr.find('td:eq(1) select').val();
                let targetDevice = tr.find('td:eq(3) select').val();
                let targetEntity = tr.find('td:eq(4) select').val();
                tr.remove();
                tbody.find('.three-way-row').each(function() {
                    if ($(this).find('td:eq(0) select').val() === targetDevice &&
                        $(this).find('td:eq(1) select').val() === targetEntity &&
                        $(this).find('td:eq(3) select').val() === sourceDevice &&
                        $(this).find('td:eq(4) select').val() === sourceEntity) {
                        $(this).remove();
                    }
                });
                highlightDuplicateRows();
            });

            tr.find('select').change(highlightDuplicateRows); // Highlight rows on any dropdown change
        });
    }

    $('#add-mapping-btn').click(function() {
        addMappingRow();
    });

    $('#save-mappings-btn').click(function() {
        let mappings = [];
        let valid = true;
        $('#mappings-table tbody tr').each(function() {
            let source_device = $(this).find('td:eq(0) select').val();
            let source_entity_id = $(this).find('td:eq(1) select').val();
            let target_device = $(this).find('td:eq(3) select').val();
            let target_entity_id = $(this).find('td:eq(4) select').val();
            
            if (source_device === target_device && source_entity_id === target_entity_id) {
                showMessage('warning', 'Source and target entities cannot be the same.');
                valid = false;
                return false; // break the loop
            }
            
            mappings.push({ source_device, source_entity_id, target_device, target_entity_id });
        });

        if (!valid) {
            return;
        }

        showSpinner();
        $.ajax({
            url: '/save_mappings',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ mappings: mappings }),
            success: function(response) {
                showMessage('success', response.message);
            },
            error: function(response) {
                showMessage('warning', response.responseJSON.message);
            },
            complete: function() {
                hideSpinner();
            }
        });
    });

    function loadMappingsTable() {
        $.get('/get_mappings', function(data) {
            let tbody = $('#mappings-table tbody');
            tbody.empty(); // Clear existing rows
    
            if (data.mappings.length === 0) {
                addMappingRow(); // Add an empty row if there are no mappings
            }
    
            data.mappings.forEach(mapping => {
                addMappingRow({
                    source_device: mapping.source_device,
                    source_entity_id: mapping.source_entity_id,
                    target_device: mapping.target_device,
                    target_entity_id: mapping.target_entity_id,
                    three_way: mapping.three_way === 'true'
                });
            });
    
            highlightDuplicateRows();
        }).fail(function(response) {
            console.log('Failed to load mappings:', response);
            showMessage('warning', 'Failed to load mappings.');
        });
    }    
    
    $('#run-main-btn').click(function() {
        showSpinner();
        $.post('/run_main', function(response) {
            showMessage('success', response.message);
        }).fail(function(response) {
            showMessage('warning', response.responseJSON.message);
        }).always(function() {
            hideSpinner();
        });
    });    

    loadMappingsTable();

    // Highlight the selected tab
    if (window.location.pathname.endsWith('/mappings')) {
        $('#nav-mappings').addClass('active');
        $('#nav-devices').removeClass('active');
        $('#nav-settings').removeClass('active');
    } else if (window.location.pathname.endsWith('/devices')) {
        $('#nav-devices').addClass('active');
        $('#nav-mappings').removeClass('active');
        $('#nav-settings').removeClass('active');
        loadDevicesTable(); // Load devices.csv automatically if it exists
    } else if (window.location.pathname.endsWith('/settings')) {
        $('#nav-settings').addClass('active');
        $('#nav-devices').removeClass('active');
        $('#nav-mappings').removeClass('active');
    }

    // Load devices.csv automatically if it exists and populate the devices table
    function loadDevicesTable() {
        $.get('/devices.csv', function(data) {
            if (data) {
                // Parse CSV data and populate the devices table
                let devices = $.csv.toObjects(data);
                devices.forEach(device => {
                    let tr = $('<tr></tr>');
                    tr.append(`<td>${device.device}</td>`);
                    tr.append(`<td>${device.entity_id}</td>`);
                    $('#devices-table tbody').append(tr);
                });
            }
        }).fail(function(response) {
            showMessage('warning', 'devices.csv file not found. Please fetch devices first.');
        });
    }

    $('#fetch-devices-btn').click(function() {
        showSpinner();
        console.log("Fetch devices button clicked");
        $.post('/fetch_devices', function(response) {
            console.log("Fetch devices response:", response);
            showMessage('success', response.message);
            hideSpinner();
        }).fail(function(response) {
            console.log("Fetch devices error response:", response);
            showMessage('warning', response.responseJSON.message);
            hideSpinner();
        });
    });
});
