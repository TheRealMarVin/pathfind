from helpers.log_helpers import compare_experiment_folders


def main(path_1, path_2):
    same = compare_experiment_folders(path_1, path_2)
    print("Equivalent" if same else "Different")


if __name__ == "__main__":
    folder_1 = "output/single_map_config_no_obstacles-2025-06-15_19-35-46"
    folder_2 = "output/single_map_config_no_obstacles-2025-06-15_20-02-02"
    main(folder_1, folder_2)