/*jshint esversion: 6 */
/*jshint browser: true */
/*jshint node: true */
"use strict";
var currentPosition = 0;

function addCheck(element) {
    element.style.backgroundColor = '#aaffaa';
}

function createTableRow(productName = '', price = 0, count = 1) {


    currentPosition++;
    var data = {
        positions: currentPosition,
        selectedProducts: [],
        priceChangesProducts: [],
    };
    var containerId = "selected_products";
    const newRow = createRowHTML(productName, price, count, currentPosition, containerId);
    const table = document.querySelector("#" + containerId);
    console.log(newRow);
    if (table.lastElementChild) {
        table.appendChild(newRow);
    } else {
        table.insertBefore(newRow, table.firstElementChild.nextSibling);
    }

    updateProductData( newRow, data);
    updateTotalSum();

    addEventListenersForProduct(newRow, data, currentPosition);
}

function createRowHTML(productName, price, count, positions, containerId) {
    const sumProduct = parseFloat(price) * parseFloat(count) || 0;

    const newRow = document.createElement("tr");
    newRow.id = "position" + positions;
    newRow.innerHTML = `
    <table class="${containerId}">
      <td class="number_position grey_cell products__line" readonly>${positions}</td>
      <td contentEditable="true" class="products__line" type="text"></td>
      <td contentEditable="true" class="products__line" type="text">${productName}</td>
      <td contentEditable="true" class="products__line" type="text">${count}</td>
      <td contentEditable="true" class="products__line" type="text"></td>
      <td contentEditable="true" class="products__line" type="text">${price}</td>
      <td class="grey_cell products__line" type="text">${sumProduct}</td>
      <td contentEditable="true" class="products__line" type="text"></td>
      <td class="delete-icon-text" style="cursor: pointer" onclick="deletePosition(${positions})">
        <img class="delete-icon" src="/static/lk_files/delete_x.svg" alt="">
      </td>
      <td contentEditable="true" class="products__line" type="text"></td>
      <td class="grey_cell products__line" type="text" value=""></td>
      <td contentEditable="true" class="products__line" type="text" value=""></td>
      <td data-price="${price}" class="products__line hidden" type="text"></td>
    </table>`;
    return newRow;
}


function updateTotalSum() {
    const inputNdc = 20;
    let totalSum = 0;

    const rows = document.querySelectorAll("#selected_products tr[id^='position']");
    const dictPriceChangesProducts = {};

    rows.forEach(row => {
        const priceCell = row.querySelector('td.products__line:nth-child(6)');
        const quantityCell = row.querySelector('td.products__line:nth-child(4)');
        const sumCell = row.querySelector('td.products__line:nth-child(7)');

        const price = parseFloat(priceCell.textContent);
        const quantity = parseFloat(quantityCell.textContent) || 1;
        const sumProduct = price * quantity;

        sumCell.textContent = sumProduct;
        totalSum += sumProduct;
    });

    const ndc = (totalSum * inputNdc) / 100;
    const totalSumAndNdc = totalSum + ndc;

    dictPriceChangesProducts.totalSum = Math.floor(totalSum);
    dictPriceChangesProducts.ndc = Math.floor(ndc);
    dictPriceChangesProducts.totalSumAndNdc = Math.floor(totalSumAndNdc);

    document.querySelector('.total__sum-value').textContent = dictPriceChangesProducts.totalSum;
    document.querySelector('.total__sum-value_ndc').textContent = dictPriceChangesProducts.ndc;
    document.querySelector('.total__sum-value_joint').textContent = dictPriceChangesProducts.totalSumAndNdc;
}

function addEventListenersForProduct(newRow, data, positions) {
    const inputWatchElementsProducts = newRow.querySelectorAll('.products__line:not(:nth-child(4)):not(:nth-child(12))');

    inputWatchElementsProducts.forEach(function (element) {
        element.addEventListener('input', function (event) {
            updateProductData(newRow, data, positions);
        });
    });

    const inputWatchElementsMarkUp = newRow.querySelectorAll('.products__line:nth-child(12)');

    inputWatchElementsMarkUp.forEach(function (element) {
        element.addEventListener('input', function (event) {
            updatePriceWithMarkup(newRow, event.target, data);
        });
    });

    const inputWatchElementsCount = newRow.querySelectorAll('.products__line:nth-child(4)');

    inputWatchElementsCount.forEach(function (element) {
        element.addEventListener('input', function () {
            updateTotalSum();
        });
    });
}

function updateProductData(row, data) {
    const position = row.querySelector('.number_position').textContent;
    const productName = row.querySelector('.products__line:nth-child(3)').textContent;
    const count = row.querySelector('.products__line:nth-child(4)').textContent;
    const price = row.querySelector('.products__line:nth-child(6)').textContent;
    const product = data.selectedProducts.find(p => p.position == position);

    if (product) {
        product.productName = productName;
        product.count = count;
        product.price = price;
    } else {
        data.selectedProducts.push({
            position: position,
            productName: productName,
            count: count,
            price: price
        });
    }

    updateTotalSum();
}

function updatePriceWithMarkup(row, targetElement, data) {
    console.log(('test_markup'));
    const position = row.querySelector('.number_position').textContent;
    var priceBase = parseFloat(row.querySelector('.products__line.hidden').getAttribute('data-price')) || 0;
    if (priceBase == 0) {
        priceBase = parseFloat(row.querySelector('.products__line:nth-child(6)').textContent) || 0;
    }
    const count = row.querySelector('.products__line:nth-child(4)').textContent;
    const pricePercent = parseInt(targetElement.textContent);

    let price = Math.round(parseInt(priceBase) * (1 + pricePercent / 100));

    const productIndex = data.selectedProducts.findIndex(p => p.position == position);
    if (productIndex !== -1) {
        if (isNaN(price) || price < priceBase || pricePercent <= 0) {
            price = priceBase;
        }
        data.selectedProducts[productIndex].price = price;
        row.querySelector('.products__line:nth-child(6)').textContent = price;

        const sumProduct = (parseInt(price) * parseInt(count)).toFixed(2);
        row.querySelector('.products__line:nth-child(7)').textContent = sumProduct;

        updateTotalSum();
    } else {
        console.log('Product with position ' + position + ' not found in selectedProducts.');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const totalSumAndNdcElement = document.querySelector('.total__sum-value_joint');
    const secondStringWithPriceInWordsElement = document.querySelector('.secondStringWithPriceInWords');
    const firstStringWithPriceInWordsElement = document.querySelector('.firstStringWithPriceInWords');
    const markupInput = document.getElementById("markupInput");

    const observer = new MutationObserver(() => {
        updateNumberToString(totalSumAndNdcElement, secondStringWithPriceInWordsElement, firstStringWithPriceInWordsElement);
    });

    const config = { childList: true };

    observer.observe(totalSumAndNdcElement, config);

    markupInput.addEventListener('input', () => {
        updateMarkupInput(markupInput);
    });
});

function updateNumberToString(element, secondStringWithPriceInWords, firstStringWithPriceInWords) {
    const newValue = element.textContent;
    const resultNumberToWords = numberToString(newValue);

    secondStringWithPriceInWords.textContent = resultNumberToWords;
    const textFooterSum = `Всего наименований  ${currentPosition}, на сумму ${newValue} руб.`;
    firstStringWithPriceInWords.textContent = textFooterSum;

    updateTotalSum();
}

function updateMarkupInput(input) {
    const markup = parseFloat(input.value) || 0;
    const markupElements = document.querySelectorAll('.products__line:nth-child(12)');

    markupElements.forEach((element) => {
        element.textContent = markup;
    });

    const priceElements = document.querySelectorAll('.products__line:nth-child(6)');

    priceElements.forEach(function (element) {

        var priceBase = parseFloat(element.parentElement.querySelector('.products__line.hidden').getAttribute('data-price'))|| 0;
        if (priceBase == 0) {
        priceBase = parseFloat(element.parentElement.querySelector('.products__line:nth-child(6)').textContent) || 0;
    }
        element.textContent = parseInt(priceBase);
        const newPrice = Math.round(parseInt(element.textContent) + (parseInt(element.textContent) * markup) / 100);
        element.textContent = newPrice;
    });

    updateTotalSum();
}

function collectProductData() {
    const rows = document.querySelectorAll("#selected_products tr[id^='position']");
    const productData = [];

    rows.forEach((row) => {
        const columns = row.querySelectorAll('.products__line');

        const product = {
            position: columns[0].textContent,
            article: columns[1].textContent,
            productName: columns[2].textContent,
            count: columns[3].textContent,
            unit: columns[4].textContent,
            price: columns[5].textContent,
            amount: columns[6].textContent,
            note: columns[7].textContent,
        };

        productData.push(product);
    });

    return productData;
}

function deletePosition(position) {
    $('#position' + position).remove();

    const rows = document.querySelectorAll("#selected_products tr[id^='position']");
    let newPosition = 1;

    rows.forEach((row) => {
        row.querySelector('.number_position').textContent = newPosition;
        newPosition++;
    });
}


document.getElementById("generate-pdf-button").addEventListener("click", generatePdf);

function generatePdf() {
    const sourceElement = document.querySelector('.total__company-name-title-head.editable_element');
    const companyInfo = sourceElement.innerHTML;
    const titleElement = document.querySelector('.total__title.editable_element');
    const title = titleElement.textContent;
    const supplierElement = document.querySelector('.supplierElement.editable_element');
    const supplier = supplierElement.textContent;
    const buyerElement = document.querySelector('.buyerElement.editable_element');
    const buyer = buyerElement.textContent;
    const totalSumElement = document.querySelector('.total__sum-value');
    const totalSum = totalSumElement.textContent;
    const totalNdcElement = document.querySelector('.total__sum-value_ndc');
    const totalNdc = totalNdcElement.textContent;
    const totalSumJointElement = document.querySelector('.total__sum-value_joint');
    const totalSumJoint = totalSumJointElement.textContent;
    const productCostsElementFirstString = document.querySelector('.amount__words.editable_element.firstStringWithPriceInWords');
    const productCostsElementSecondString = document.querySelector('.amount__words.editable_element.secondStringWithPriceInWords');

    const productCosts = [
        {
            "totalSum": totalSum,
            "ndc": totalNdc,
            "totalSumAndNdc": totalSumJoint,
        },
        {
            "firstStringWithPriceInWords": productCostsElementFirstString.textContent,
            "secondStringWithPriceInWords": productCostsElementSecondString.textContent,

        }
    ];

    const requestData = {
        selectedProducts: collectProductData(),
        productCosts: productCosts,
        companyInfo: companyInfo,
        title: title,
        supplier: supplier,
        buyer: buyer
    };


    fetch('/generate_pdf/', {
        method: 'POST',
        body: JSON.stringify(requestData),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'PK.pdf';
        document.body.appendChild(a);
        a.click();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}













