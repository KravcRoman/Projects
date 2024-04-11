document.addEventListener("DOMContentLoaded", function() {
    const editableElements = document.querySelectorAll(".editable, .editable > span");

    function enableEditing(element) {
        element.classList.add("active");
        element.contentEditable = "true";
        element.focus();
    }

    function disableEditing(element) {
        element.classList.remove("active");
        element.contentEditable = "false";
    }

    editableElements.forEach((element) => {
        element.addEventListener("click", function() {
            if (element.contentEditable !== "true") {
                enableEditing(element);
            }
        });

        element.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                disableEditing(element);
            }
        });
    });

    document.addEventListener("click", function(event) {
        editableElements.forEach((element) => {
            if (element.contentEditable === "true" && event.target !== element) {
                disableEditing(element);
            }
        });
    });
});

var positions = 0;
var markupInput = document.getElementById("markupInput");

function hideResults() {
    $("#product-results").empty();
    $("#category-results").empty();
    $('.search-data').hide();
    $('.not-search-data').show();
}

function showResults() {
    $('.search-data').show();
    $('.not-search-data').hide();
}

function deletePosition(position) {
    $('#position' + position).remove();
    refreshDocument();
}
var editableCell = document.getElementById("editableCell");

var markupCell = document.getElementById("markupCell");


function addSelectedProduct(productName, price, remark) {

    if (price === undefined) {
        price = '';
    }
     if (remark === undefined) {
        remark= '';
    }
    positions = positions + 1;

    var new_num = $('#selected_products tr:last td:first').text();
    if (new_num != '') {
      new_num = (parseInt($('#selected_products tr:last td:first').text()) + 1);
    } else {
      new_num = 1;
    }

    createTableRow(productName, price, 1);

    /*
    $('#selected_products tr:last')
        .after('<tr id="position_' + new_num + '">' +
            '<td class="number_position grey_cell products__line" readonly="">' + new_num + '</td>' +

            '<td contenteditable="true" class="products__line" type="text"></td>' +
            '<td contenteditable="true" class="products__line" type="text">' + productName + '</td>' +
            '<td contenteditable="true" class="products__line" type="text">1</td>' +

            '<td contenteditable="true" class="products__line" type="text"></td>' +
            '<td contenteditable="true" class="products__line" type="text">' + price + '</td>' +
            '<td class="grey_cell products__line" type="text">0</td>' +
            '<td contenteditable="true" class="products__line" type="text"></td>' +
            '<td class="delete-icon-text" style="cursor: pointer" onclick="deletePosition(1)">' +
            '<img class="delete-icon" src="/static/lk_files/delete_x.svg" alt="">' +
            '</td>' +
            '<td contenteditable="true" class="products__line" type="text"></td>' +
            '<td class="grey_cell products__line" type="text" value=""></td>' +
            '<td contenteditable="true" class="products__line" type="text" value=""></td>' +
            '<td data-price="0" class="products__line hidden" type="text"></td>' +
            '</tr>'
        );
        */

    $('.input_watch').keyup(function() {
        refreshDocument();
    });

    refreshDocument();

    var data = {
        positions: currentPosition,
        selectedProducts: [],
        priceChangesProducts: [],
    };

    updateTotalSum();

    addEventListenersForProduct($('#selected_products tr:last'), data,  currentPosition);
}

function refreshDocument() {

    var totalSum = 0;
    var totalSum_and_ndc = 0;
    var input_ndc = 20;
    var markup = parseFloat(markupInput.value) || 0;
    var html = '<tr class="total__table-row">' +
        '<th class="total__table-th">№</th>' +
        '<th class="total__table-th">Товары (работы, услуги)</th>' +
        '<th class="total__table-th">Цена</th>' +
        '<th class="total__table-th">Кол-во</th>' +
        '<th class="total__table-th">Ед.</th>' +
        '<th class="total__table-th">Сумма</th>' +
        '<th class="total__table-th">--------</th>' +
        '<th class="total__table-th"> Наценка % </th>' +
        '<th class="total__table-th"> Примечание </th>' +
    '</tr>';

    var num = 0;
    $('#selected_products tr').not(':first').not(':last').each(function(tr_index) {
        var trHtml = '<tr class="total__table-row">';

        num += 1;
        trHtml += '<td class="total__table-td">' + num + '</td>';
        var price = $(this).find('td input').eq(1).val();
        var quantity = $(this).find('td input').eq(2).val() || 1;
        var basePrice = parseFloat(price);
        var markup = $(this).find('td input[placeholder="Наценка"]').val() ||  parseFloat(markupInput.value) || 0;
        var calculatedPrice = basePrice * (1 + (markup / 100));

        var remark = $(this).find('td input[placeholder="Комментарий"]').val();

        calculatedPrice = calculatedPrice.toFixed();
        totalSum += calculatedPrice * quantity;

        $(this).find('td input').each(function(td_index) {
            if (td_index === 1) {
                trHtml += '<td class="total__table-td">' + calculatedPrice + '</td>';
            } else if (td_index === 4) {
                trHtml += '<td class="total__table-td">' + (calculatedPrice * quantity) + '</td>';
            } else {
                trHtml += '<td class="total__table-td">' + $(this).val() + '</td>';
            }
        });

        ndc = (totalSum * input_ndc) / 100;
        totalSum_and_ndc = totalSum + (totalSum * input_ndc) / 100;
        $('.total__sum-value').text(totalSum.toFixed(2));
        $('.total__sum-value_ndc').text(ndc.toFixed(2));
        $('.total__sum-value_final').text(totalSum_and_ndc.toFixed(2));

        trHtml += '<td class="total__table-td editable-markup">' + markup + '</td>';
        trHtml += '<td class="total__table-td editable-remark">' + remark + '</td>';

        html += trHtml + '</tr>';
    });

    $('#total_table').html(html);
    refreshTotal();
}

function refreshTotal() {
}

function addCheck(element) {
    //$(element).append('<img class="td-selected" src="https://prod.pkf-m.ru/static/images/positions/check.svg" alt="">');
    $(element).css('background-color', '#aaffaa');
}