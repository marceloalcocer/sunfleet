import enum
import numpy as np
import matplotlib.pyplot as plt

# S = S^{car}_{i_plan,i_car,i_time}(t,x) + S^{plan}_{i_plan}
#
# i_plan = one, small, medium, large
# i_car = liten, medium, stor
# i_time = day, night
#


class Plan:
	"""Sunfleet membership plan class"""

	name = None
	"""Membership plan name"""

	fee = None
	"""Monthly membership plan fee [SEK]"""

	rates = None
	"""Rental rates [SEK]"""

	def __init__(self, name, fee, rates):
		self.name = name
		self.fee = fee
		self.rates = rates

	def price_pro_rata(self, car, time, hours, kms):
		"""Pro-rate rental price
		
		Price of a journey (in SEK) billed under a pro-rata pricing scheme (per hour,
		per km)
		
		:param str car: The class of car rented. Allowed values "elbil", "liten",
		"mellan", "stor", "premium", "transport_liten", "transport_stor"
		:param str time: Time of day for rental. Allowed values "day", "night"
		:param hours: Duration of rental (in hours)
		:param kms: Distance travelled (in km)
		:return: The total rental price in SEK
		
		"""

		rate = self.rates[car]
		price = 0

		# Times cost
		price += rate["hour"][time] * hours

		# Distance cost
		price += rate["km"] * kms

		# Return
		return price


# Current plans (2018.01.04)
plans = (
	Plan(
		name="one",
		fee=0,
		rates={
			"elbil": {"hour":{"day":70, "night": 70}, "km": 2, "day": 549, "weekend": 749},
			"liten": {"hour":{"day":80, "night": 80}, "km": 2, "day": 589, "weekend": 769},
			"mellan": {"hour":{"day":90, "night": 90}, "km": 2, "day": 709, "weekend": 869},
			"stor": {"hour":{"day":100, "night": 100}, "km": 2, "day": 829, "weekend": 1069},
			"premium": {"hour":{"day":140, "night": 140}, "km": 2, "day": 1249, "weekend": 1849},
			"transport_liten": {"hour":{"day":110, "night": 110}, "km": 2, "day": 949, "weekend": 1169},
			"transport_stor": {"hour":{"day":180, "night": 180}, "km": 2, "day": 1819, "weekend": None}
		}
	),
	Plan(
		name="small",
		fee=169,
		rates={
			"elbil": {"hour": {"day":30, "night": 30}, "km": 2, "day": 349, "weekend": 549},
			"liten": {"hour": {"day":40, "night": 40}, "km": 2, "day": 389, "weekend": 569},
			"mellan": {"hour": {"day":50, "night": 50}, "km": 2, "day": 509, "weekend": 669},
			"stor": {"hour": {"day":60, "night": 60}, "km": 2, "day": 629, "weekend": 869},
			"premium": {"hour": {"day":100, "night": 100}, "km": 2, "day": 1049, "weekend": 1649},
			"transport_liten": {"hour": {"day": 70, "night": 70}, "km": 2, "day": 749, "weekend": 969},
			"transport_stor": {"hour": {"day": 140, "night": 140}, "km": 2, "day": 1619, "weekend": None}
		}
	),
	Plan(
		name="medium",
		fee=499,
		rates={
			"elbil": {"hour": {"day": 20, "night": 0}, "km": 1, "day": 299, "weekend": 479},
			"liten": {"hour": {"day": 30, "night": 0}, "km": 1, "day": 339, "weekend": 499},
			"mellan": {"hour": {"day": 40, "night": 0}, "km": 1, "day": 459, "weekend": 599},
			"stor": {"hour": {"day": 50, "night": 0}, "km": 1, "day": 579, "weekend": 799},
			"premium": {"hour": {"day": 90, "night": 0}, "km": 1, "day": 999, "weekend": 1559},
			"transport_liten": {"hour": {"day": 60, "night": 0}, "km": 1, "day": 699, "weekend": 899},
			"transport_stor": {"hour": {"day": 130, "night": 0}, "km": 1, "day": 1539, "weekend": None}
		}
	),
	Plan(
		name="large",
		fee=999,
		rates={
			"elbil": {"hour": {"day": 15, "night": 0}, "km": 1, "day": 249, "weekend": 399},
			"liten": {"hour": {"day": 15, "night": 0}, "km": 1, "day": 249, "weekend": 399},
			"mellan": {"hour": {"day": 25, "night": 0}, "km": 1, "day": 369, "weekend": 499},
			"stor": {"hour": {"day": 35, "night": 0}, "km": 1, "day": 489, "weekend": 599},
			"premium": {"hour": {"day": 75, "night": 0}, "km": 1, "day": 909, "weekend": 1299},
			"transport_liten": {"hour": {"day": 45, "night": 0}, "km": 1, "day": 609, "weekend": 699},
			"transport_stor": {"hour": {"day": 115, "night": 0}, "km": 1, "day": 1439, "weekend": None}
		}
	)
)


def compute_cheapest_pro_rata(car, time, hours, kms):
	"""Compute cheapest monthly price for pro-rata rentals
	
	If rental is only done on a pro-rata scheme and always renting the same class of
	car at the same time of day, the total monthly expenditure, :math:`C`, is given by,
	
	.. math::
	
		C = C^{pro-rata}_{plan,car,time}(t,x) + C^{plan}_{plan}
		
	where `t` is the total rental duration (over 1 month), `x` the total
	distance travelled (over 1 month) and `plan`, `car`, `time` index the
	membership plan, rented car class, and time of day respectively.
	
	For any given combination of car class and time-of day, the plan yielding the
	minimum monthly expenditure therefore depends on the total renatal duration
	and distance, and is found by minimising over the `plan` dimension.

	:param str car: The class of car rented. Allowed values "elbil", "liten",
	"mellan", "stor", "premium", "transport_liten", "transport_stor"
	:param str time: Time of day for rental. Allowed values "day", "night"
	:param hours: Duration of rental (in hours)
	:type hours: 1D array
	:param kms: Distance travelled (in km)
	:type kms: 1D array
	:return: Cheapest monthly price and corresponding plan
	:rtype: 2-tuple of 2D ndarrays
	
	"""

	# Compute all journey prices
	costs = []
	for plan in plans:
		costs.append(
			[
				[
					plan.price_pro_rata(car, time, hour, km) + plan.fee for hour in hours
				] for km in kms
			]
		)
	costs = np.array(costs)

	# Compile cheapest
	plan_min = costs.argmin(axis=0)
	cost_min = costs.min(axis=0)

	# Return
	return (plan_min, cost_min)


if __name__ == "__main__":

	# Plot cheapest pro-rata price for journeys < 40 hours and < 800 km
	hours = np.linspace(0, 40, 200)
	kms = np.linspace(0, 800, 201)
	cars = ("elbil", "liten", "mellan", "stor", "premium", "transport_liten", "transport_stor")
	times = ("day", "night")
	for time in times:
		for car in cars:
			print("Plotting cheapest plan:\n\tCar: {car}\n\tTime: {time}\n\t".format(
				car=car,
				time=time
			))
			plan_min, cost_min = compute_cheapest_pro_rata(car=car, time=time, hours=hours, kms=kms)

			# Plot lowest prices
			plt.figure()
		# 	plt.pcolormesh(
			plt.contourf(
				hours,
				kms,
				cost_min,
				vmin=0,
				vmax=4000
			)
			plt.set_cmap("viridis")
			plt.colorbar()

			# Plot cheapest plan
			cs = plt.contour(
				hours,
				kms,
				plan_min,
				range(len(plans)),
				colors="w"
			)
			fmt = {
				level:plan for level, plan in zip(
					cs.levels,
					[plan.name for plan in plans]
				)
			}
			plt.clabel(
				cs,
				cs.levels,
				fmt=fmt,
				inline_spacing=10
			)

			# Plot speed limits
			style = {
				"color": (0 ,) * 3,
		# 		"linestyle":"--"
			}
			plt.plot(
				hours, 120 * hours,
				label="120 km/h",
				linestyle="--",
				** style
			)
			plt.plot(
				hours, 70 * hours,
				label="70 km/h",
				linestyle="-.",
				** style
			)
			plt.plot(
				hours, 50 * hours,
				label="50 km/h",
				linestyle=":",
				** style
			)
			plt.legend(
				loc="upper center",
				fontsize=12,
				frameon=False,
		# 		framealpha=0.6
			)

			# Formatting
			plt.xlim(hours[0], hours[-1])
			plt.ylim(kms[0], kms[-1])
			plt.xlabel("Times [hours/month]")
			plt.ylabel("Distance [km/month]")
			plt.title("Minimum cost [SEK/month]")

			# Formatting
			bbox_props = {
				"boxstyle": "square",
				"fc": "w",
				"ec": "k"
			}
			plt.gca().text(
				1,
				780,
				"Car: \"{car}\"\nTime of day: \"{time}\"".format(car=car, time=time),
				ha="left",
				va="top",
				bbox=bbox_props
			)

			# Save
	# 		plt.show()
			plt.savefig(
				"sunfleet_{car}_{time}.png".format(car=car, time=time),
				dpi=150
			)
			plt.clf()

