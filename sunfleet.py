import enum
import numpy as np
import matplotlib.pyplot as plt

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

	def price_pro_rata(self, car, hours, kms):
		"""Pro-rate rental price
		
		Price of a journey (in SEK) billed under a pro-rata pricing scheme (per hour,
		per km)
		
		:param str car: The class of car rented. Allowed values "elbil", "liten",
		"mellan", "stor", "premium", "transport_liten", "transport_stor"
		:param hours: Duration of rental (in hours)
		:param kms: Distance travelled (in km)
		:return: The total rental price in SEK
		
		"""

		rate = self.rates[car]
		price = 0

		# Times cost
		price += rate["hour"] * hours

		# Distance cost
		price += rate["km"] * kms

		# Return
		return price


# Current plans (2018.07.30)
plans = (
	Plan(
		name="one",
		fee=0,
		rates={
			"liten": {"hour": 80, "km": 2, "day": 589, "weekend": 869},
			"mellan": {"hour": 100, "km": 2, "day": 829, "weekend": 1069},
			"stor": {"hour": 120, "km": 2, "day": 1049, "weekend": 1469},
			"premium": {"hour": 140, "km": 2, "day": 1249, "weekend": 1869},
			"transport_liten": {"hour": 110, "km": 2, "day": 969, "weekend": None},
			"transport_mellan": {"hour": 160, "km": 2, "day": 1569, "weekend": None},
			"transport_stor": {"hour": 180, "km": 2, "day": 1769, "weekend": None}
		}
	),
	Plan(
		name="small",
		fee=169,
		rates={
			"liten": {"hour": 40, "km": 2, "day": 389, "weekend": 669},
			"mellan": {"hour": 60, "km": 2, "day": 629, "weekend": 869},
			"stor": {"hour": 80, "km": 2, "day": 849, "weekend": 1269},
			"premium": {"hour": 100, "km": 2, "day": 1049, "weekend": 1669},
			"transport_liten": {"hour": 70, "km": 2, "day": 769, "weekend": None},
			"transport_mellan": {"hour": 130, "km": 2, "day": 1369, "weekend": None},
			"transport_stor": {"hour": 150, "km": 2, "day": 1569, "weekend": None}
		}
	),
	Plan(
		name="medium",
		fee=499,
		rates={
			"liten": {"hour": 30, "km": 1, "day": 339, "weekend": 599},
			"mellan": {"hour": 50, "km": 1, "day": 579, "weekend": 799},
			"stor": {"hour": 70, "km": 1, "day": 799, "weekend": 1199},
			"premium": {"hour": 90, "km": 1, "day": 999, "weekend": 1599},
			"transport_liten": {"hour": 60, "km": 1, "day": 699, "weekend": None},
			"transport_mellan": {"hour": 120, "km": 1, "day": 1299, "weekend": None},
			"transport_stor": {"hour": 140, "km": 1, "day": 1499, "weekend": None}
		}
	),
	Plan(
		name="large",
		fee=999,
		rates={
			"liten": {"hour": 15, "km": 1, "day": 249, "weekend": 489},
			"mellan": {"hour": 35, "km": 1, "day": 489, "weekend": 599},
			"stor": {"hour": 55, "km": 1, "day": 659, "weekend": 899},
			"premium": {"hour": 75, "km": 1, "day": 909, "weekend": 1299},
			"transport_liten": {"hour": 45, "km": 1, "day": 609, "weekend": None},
			"transport_mellan": {"hour": 105, "km": 1, "day": 1199, "weekend": None},
			"transport_stor": {"hour": 125, "km": 1, "day": 1399, "weekend": None}
		}
	)
)


def compute_cheapest_pro_rata(car, hours, kms):
	"""Compute cheapest monthly price for pro-rata rentals
	
	If rental is only done on a pro-rata scheme and always renting the same class of
	car, the total monthly expenditure, :math:`C`, is given by,
	
	.. math::
	
		C = C^{pro-rata}_{plan,car}(t,x) + C^{plan}_{plan}
		
	where `t` is the total rental duration (over 1 month), `x` the total
	distance travelled (over 1 month) and `plan` and `car` index the
	membership plan and rented car class respectively.
	
	For any car class, the plan yielding the minimum monthly expenditure
	therefore depends on the total renatal duration and distance, and is
	found by minimising over the `plan` dimension.

	:param str car: The class of car rented. Allowed values are "liten",
	"mellan", "stor", "premium", "transport_liten", "transport_mellan",
	"transport_stor"
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
					plan.price_pro_rata(car, hour, km) + plan.fee for hour in hours
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
	cars = (
		"liten",
		"mellan",
		"stor",
		"premium",
		"transport_liten",
		"transport_mellan",
		"transport_stor"
	)
	for car in cars:
		print("Plotting cheapest plan:\n\tCar: {car}\n\t".format( car=car))
		plan_min, cost_min = compute_cheapest_pro_rata(car=car, hours=hours, kms=kms)

		# Plot lowest prices
		plt.figure()
		vlims = (0, 7000)
		plt.contourf(
			hours,
			kms,
			cost_min,
			vmin=vlims[0],
			vmax=vlims[1]
		)
		plt.set_cmap("viridis")
		plt.colorbar()

		# Plot cheapest plan
		cs = plt.contour(
			hours,
			kms,
			plan_min,
			[x + 0.5 for x in range(len(plans))],
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
			"color": (0 ,) * 3
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
			"Car: \"{car}\"".format(car=car),
			ha="left",
			va="top",
			bbox=bbox_props
		)

		# Save
		plt.savefig(
			"sunfleet_{car}.png".format(car=car),
			dpi=150
		)
		plt.clf()

