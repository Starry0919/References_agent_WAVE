def map_steps(steps):
    result = {"design": [], "build": [], "test": [], "learn": []}
    for step in steps: result[step["phase"]].append(step)
    return result
