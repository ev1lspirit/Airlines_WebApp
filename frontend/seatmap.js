var firstSeatLabel = 1;

			$(document).ready(function() {
				var $cart = $('#selected-seats'),
					$counter = $('#counter'),
					$total = $('#total'),
					sc = $('#seat-map').seatCharts({
					map: [
            'ppppppppppppppppppppppppppppppppppppp_______________________',
						'',
            'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk',
            'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj',
            '',
            '___________iiiiiiiiiiiiiiiiiiiii',
            '___________hhhhhhhhhhhhhhhhhhhhh',
            '___________ggggggggggggggggggggg',
            '', 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
					],
					seats: {
            p: {
							price   : 5000,
							classes : 'vip-class',
							category: 'VIP Ticket'
						},
            k: {
							price   : 2500,
							classes : 'standard-balcony-class',
							category: 'Standard Ticket (Balcony)'
						},
            j: {
							price   : 2500,
							classes : 'standard-balcony-class',
							category: 'Standard Ticket (Balcony)'
						},
            i: {
							price   : 2500,
							classes : 'standard-ground-class',
							category: 'Standard Ticket (Ground)'
						},
            h: {
							price   : 2500,
							classes : 'standard-ground-class',
							category: 'Standard Ticket (Ground)'
						},
            g: {
							price   : 2500,
							classes : 'standard-ground-class',
							category: 'Standard Ticket (Ground)'
						},
            c: {
							price   : 1250,
							classes : 'student-class',
							category: 'Student Ticket'
						},
					
					},
					naming : {
            rows: ['P','','K','J','','I','H','G','','C'],
						top : false,
						getLabel : function (character, row, column) {
              if (row == 'P') {
                return column;
              } else if (row == 'K' || row == 'J') {
                return column;
              } else if (row == 'I' || row == 'H' || row == 'G') {
                return column;
              } else if (row == 'C') {
                return column;
              }
						},
					},
					legend : {
						node : $('#legend'),
					    items : [
                [ 'p', 'available',   'VIP Ticket' ],
                [ 'k', 'available',   'Standard Ticket (Balcony)' ],
                [ 'i', 'available',   'Standard Ticket (Ground)'],
                [ 'c', 'available', 'Student Ticket'],
                [ 'f', 'unavailable', 'Already Booked']
					    ]					
					},
					click: function () {
						if (this.status() == 'available') {
							//let's create a new <li> which we'll add to the cart items
							$('<li>'+this.data().category+' Seat # '+this.settings.label+': <b>Rs.'+this.data().price+'</b> <a href="#" class="cancel-cart-item">[cancel]</a></li>')
								.attr('id', 'cart-item-'+this.settings.id)
								.data('seatId', this.settings.id)
								.appendTo($cart);
							
							/*
							 * Lets update the counter and total
							 *
							 * .find function will not find the current seat, because it will change its stauts only after return
							 * 'selected'. This is why we have to add 1 to the length and the current seat price to the total.
							 */
							$counter.text(sc.find('selected').length+1);
							$total.text(recalculateTotal(sc)+this.data().price);
							
							return 'selected';
						} else if (this.status() == 'selected') {
							//update the counter
							$counter.text(sc.find('selected').length-1);
							//and total
							$total.text(recalculateTotal(sc)-this.data().price);
						
							//remove the item from our cart
							$('#cart-item-'+this.settings.id).remove();
						
							//seat has been vacated
							return 'available';
						} else if (this.status() == 'unavailable') {
							//seat has been already booked
							return 'unavailable';
						} else {
							return this.style();
						}
					}
				});

				//this will handle "[cancel]" link clicks
				$('#selected-seats').on('click', '.cancel-cart-item', function () {
					//let's just trigger Click event on the appropriate seat, so we don't have to repeat the logic here
					sc.get($(this).parents('li:first').data('seatId')).click();
				});

				//let's pretend some seats have already been booked
				sc.get(['1_2', '4_1', '7_1', '7_2']).status('unavailable');
		
		});

		function recalculateTotal(sc) {
			var total = 0;
		
			//basically find every selected seat and sum its price
			sc.find('selected').each(function () {
				total += this.data().price;
			});
			
			return total;
		}