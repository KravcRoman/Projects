(function () {
  'use strict'

  var clipboard = new ClipboardJS('[data-clipboard-text]');

  clipboard.on('success', function(e) {
    e.trigger.classList.remove('bi-clipboard')
    e.trigger.classList.add('bi-clipboard-check');

    setTimeout(function() {
      e.trigger.classList.remove('bi-clipboard-check')
      e.trigger.classList.add('bi-clipboard')
    }, 2000);
  });

  function loadProducts(clear) {
    var btn = $('.js-load-more-btn'),
        data = {};

    if (clear) {
      btn.data('end', false);
      btn.data('offset', 0)
    }
  
    if (btn.prop('disabled') || btn.data('end')) return;
    btn.prop('disabled', true);

    $('.product-filter input').each(function() {
      var input = $(this);
      if (input.val().trim())
        data[input.attr('name')] = input.val().trim();
    });

    data.offset = btn.data('offset') || 0;

    console.log('Request', clear, JSON.stringify(data), JSON.stringify(btn.data()));

    $.ajax({
      url: btn.data('url'),
      method: 'get',
      data: data,
    }).done(function(response) {
      console.log('Response', response.elapsed, response.next, clear, JSON.stringify(data), JSON.stringify(btn.data()))

      if (clear) {
        $('.products tbody').html('');
        btn.data('offset', 0);
      }
      
      if (response.content) {
        $('.products tbody').append(response.content);
      }
      else if (clear) {
        $('.products tbody').append(
          '<tr class="text-center"><td colspan="7">Ничего не найдено</td></tr>'
        );
      }

      btn.prop('disabled', false);
      btn.data('offset', response.offset);

      if (!response.next) {
        btn.data('end', true);
        btn.hide();
      }
    });
  }
  console.log('Init load products');
  loadProducts();
  var loadBtn = $('.js-load-more-btn');

  $('.js-load-more-btn').click(function() {
    console.log('Click load products', JSON.stringify(loadBtn.data()));
    loadProducts()
  });

  var inputCounter = 0;

  $('.product-filter input').on('keyup change', function() {
    var input = $(this),
        value = input.val().trim();

    if (value === input.data('value')) {
      return
    }

    input.data('value', value)
    input.next().toggle(value != '');
    inputCounter++;
    var counter = inputCounter;

    console.log('Filter', counter, inputCounter, value, JSON.stringify(loadBtn.data()));

    setTimeout(function() {
      if (inputCounter == counter) {
        loadBtn.show();
        console.log('Filter load products', counter, inputCounter, value, JSON.stringify(loadBtn.data()));
        loadProducts(true);
      }
    }, 500)
  });

  function isScrolledIntoView(el) {
    var rect = el.getBoundingClientRect();
    var elemTop = rect.top;
    var elemBottom = rect.bottom;
    var isVisible = (elemTop >= 0) && (elemBottom - 50 <= window.innerHeight);
    return false;
    //return isVisible;
  }

  if (loadBtn.length) {
    $(window).scroll(function() {
      if (!loadBtn.prop('disabled') && isScrolledIntoView(loadBtn.get(0))) {
        console.log('Scroll load products', JSON.stringify(loadBtn.data()));
        loadProducts();
      }
    });
  }

  $('.filter-field span').click(function() {
    $(this).prev().val('').trigger('change');
  });

})()
