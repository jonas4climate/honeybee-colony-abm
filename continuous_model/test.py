# # import numpy as np
# # import matplotlib.pyplot as plt
# #
# # # Define grid size
# # grid_size = 50
# # num_points = 10
# #
# # # Create an empty list to store points
# # points = []
# #
# # # Generate cluster centers
# # num_clusters = 2
# # cluster_centers = np.random.randint(0, grid_size, size=(num_clusters, 2))
# #
# # # Define clustering coefficient
# # clustering_coefficient = 0.7  # 10% of points will be around cluster centers
# #
# # # Generate points around cluster centers
# # for center in cluster_centers:
# #     for _ in range(int(num_points * clustering_coefficient / num_clusters)):
# #         points.append(center + np.random.randn(2))
# #
# # # Generate remaining points randomly in the grid
# # remaining_points = num_points - int(num_points * clustering_coefficient)
# # points.extend(np.random.randint(0, grid_size, size=(remaining_points, 2)))
# #
# # # Convert to numpy array for easy plotting
# # points = np.array(points)
# #
# # # Plot the points
# # plt.figure(figsize=(10, 10))
# # plt.scatter(points[:, 0], points[:, 1], alpha=0.6)
# # plt.title('Grid Locations with Clustering')
# # plt.xlabel('X Coordinate')
# # plt.ylabel('Y Coordinate')
# # plt.grid(True)
# # plt.show()
# import numpy as np
#
# class ModelConfig:
#     def __init__(self):
#         self.size = 10_000
#
# def cluster_resources(self, n_resources, n_clusters, clust_coeff=0.5):
#     # Create an empty list to store locations
#     points = []
#
#     # Generate cluster centers
#     cluster_centers = np.random.randint(0, self.size, size=(n_clusters, 2))
#
#     # Generate points around cluster centers
#     for center in cluster_centers:
#         for _ in range(int(n_resources * clust_coeff / n_clusters)):
#             points.append(center + np.random.randn(2))
#
#     # Generate remaining points randomly in the grid
#     remaining_points = n_resources - int(n_resources * clust_coeff)
#     points.extend(np.random.randint(0, self.size, size=(remaining_points, 2)))
#
#     # Convert to numpy array for easy plotting
#     resource_location = np.array(points)
#
#     # for 1 hive, place at center
#     hive_location = [[self.size / 2, self.size / 2]]
#     return hive_location, resource_location
#
# hive_loc, resource_loc = cluster_resources(ModelConfig(), 10, 2, 1)
# resource_loc[0]
#
# pos, pos = resource_loc[0]
#
#
#
#
#
#
#
#
#
#
# from random import shuffle
# # @staticmethod
# def init_space(width, height, n_resources, n_hives):
#     """Initialize the space with resources and hives."""
#     positions = [(x, y) for x in range(0, width, 10) for y in range(0, height, 10)]
#
#     shuffle(positions)
#
#     resource_location = positions[0:n_resources]
#     if n_hives != 1:
#         i_hives = n_resources + n_hives
#         hive_location = [positions[n_resources:i_hives]]
#     else:
#         hive_location = [positions[n_resources + 1]]
#         # for 1 hive, place at center
#         hive_location = [[width/2, height/2]]
#     return hive_location, resource_location
#
# # @staticmethod
# def cluster_resources(size, n_resources, n_clusters, clust_coeff=0.5):
#     # Create an empty list to store locations
#     resource_location = []
#     # Generate cluster centers
#     cluster_centers = np.random.randint(0, size, size=(n_clusters, 2))
#
#     # Generate resource_location around cluster centers
#     for center in cluster_centers:
#         resource_location.append(tuple(center))
#         for _ in range(int(n_resources * clust_coeff / n_clusters)):
#             point = center + np.random.randn(2)
#             resource_location.append((point[0], point[1]))
#
#     # Generate remaining resource_location randomly in the grid
#     remaining_points = n_resources - int(n_resources * clust_coeff)
#     random_points = np.random.randint(0, size, size=(remaining_points, 2))
#     for point in random_points:
#         resource_location.append((point[0], point[1]))
#
#     # for 1 hive, place at center
#     hive_location = [[size / 2, size / 2]]
#
#     return hive_location, resource_location
#
#
#
# init_space(20,20,1,1)
# hive, resource  = cluster_resources(2000, 14, 2, 0.9)
# len(resource)
#
#
#
#
#
#
#


import numpy as np


def cluster_resources(size, n_resources, n_clusters, clust_coeff):
    # Create an empty list to store locations
    resource_location = []

    # Generate cluster centers
    cluster_centers = np.random.randint(0, size, size=(n_clusters, 2))

    # Calculate the number of clustered resources
    clustered_resources = int(n_resources * clust_coeff)
    random_resources = n_resources - clustered_resources

    # Generate resource_location around cluster centers
    for center in cluster_centers:
        resource_location.append(tuple(center))
        for _ in range(int(clustered_resources / n_clusters)):
            point = center + np.random.randn(2)
            resource_location.append((point[0], point[1]))

    # Generate remaining resource_location randomly in the grid
    random_points = np.random.randint(0, size, size=(random_resources, 2))
    for point in random_points:
        resource_location.append((point[0], point[1]))

    # for 1 hive, place at center
    hive_location = [(size / 2, size / 2)]

    # Ensure the total number of resources is exactly n_resources
    resource_location = resource_location[:n_resources]

    return hive_location, resource_location


# Test the function
size = 50
n_resources = 200
n_clusters = 5
clust_coeff = 0.1

hive_location, resource_location = cluster_resources(size, n_resources, n_clusters, clust_coeff)

# Verify the number of resources
print(f"Number of resource locations: {len(resource_location)}")
