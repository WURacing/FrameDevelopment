from createBaseFrame import *
import copy
import matplotlib.pyplot as plt
import time
from loadCases import *

def sortingKey(elem):
    return elem[0]


# Important Parameters
numGenerations = 100
numSeeds = 3
numChildrenPerSeed = 5
maxNumRandTubes = 10

maxDispOfAnyTargetNode = 0.26
maxAvgDisp = 0.25
maxWeight = 60

graphUpdatePeriod = 1
plotCurrentFrame = False


# Time the simulation
start = time.time()

# Set up graphs (change size of figure's window using the first line below)
fig = plt.figure(figsize=(12,9))
fig.suptitle("Genetic Simulation - Thickness")
grid = plt.GridSpec(3, 4, hspace=0.3, wspace=0.2)
ax1 = fig.add_subplot(grid[0, :2], title="Score/Weight vs Generations")
ax1.set_ylabel('Objective Function Score')
ax2 = fig.add_subplot(grid[1, :2], title="Avg Displacement vs Generations")
ax2.set_ylabel('Inches')
ax3 = fig.add_subplot(grid[2, :2], title="Weight vs Generations")
ax3.set_ylabel('Pounds')
if plotCurrentFrame:
    ax4 = fig.add_subplot(grid[1:, 2:], title="Maximum Frame", projection='3d')
    ax5 = fig.add_subplot(grid[0, 2:], title="Current Frame", projection='3d')
else:
    ax4 = fig.add_subplot(grid[0:, 2:], title="Maximum Frame", projection='3d')
ax1.grid()
ax2.grid()
ax3.grid()


# Initialize variables
maxScorePerWeight = 0
averageDisp = 0

maxScoresPerWeight = []
weights = []
averageDisps = []
iterations = []



baseFrame = createBaseFrame()
baseFrameScorePerWeight, dispList, baseFrameAvgDisp = baseFrame.solveAllLoadCases()
print("\nBase Frame Weight:", baseFrame.weight)
print("Base Frame Score:", baseFrameScorePerWeight)
print("Base Frame Avg. Disp.:", baseFrameAvgDisp)
print("Base Frame Max Disp of A Target Node:", max(dispList))

maxScoresPerWeight.append(baseFrameScorePerWeight)
weights.append(baseFrame.weight)
averageDisps.append(baseFrameAvgDisp)
iterations.append(0)



maxFrame = baseFrame
errorFlag = False
seeds = []
for i in range(numSeeds):
    seeds.append(maxFrame)

ax1.plot(iterations, maxScoresPerWeight)
ax2.plot(iterations, averageDisps)
ax3.plot(iterations, weights)
maxFrame.plotAni(ax4)
fig.suptitle("Starting in 3")
plt.pause(1)
fig.suptitle("Starting in 2")
plt.pause(1)
fig.suptitle("Starting in 1")
plt.pause(1)
fig.suptitle("Genetic Simulation - Thickness")
plt.pause(.001)

print("\n--START--")
# Run the simulation with multithreading
for gen in range(1, numGenerations+1):
    # Generate generation individuals
    if gen is 1:
        startOneFrame = time.time()
    individuals = []
    for seed in seeds:
        theSameInd = copy.deepcopy(seed)
        individuals.append(theSameInd)
        for i in range(1, numChildrenPerSeed):
            individual = copy.deepcopy(seed)
            numRandTubes = random.randint(1,maxNumRandTubes+1)
            for j in range(numRandTubes):
                individual.randomizeThicknessOfRandomTube()
            individuals.append(individual)
            if plotCurrentFrame:
                ax5.clear()
                individual.plotAni(ax5)
                plt.pause(0.000000000000001)

    # Solve generation individuals
    sortingList = []

    for i in range(len(individuals)):
        individual = individuals.__getitem__(i)
        scorePerWeight, dispList, avgDisp = individual.solveAllLoadCases()
        if (individual.weight < maxWeight and maxDispOfAnyTargetNode > max(dispList) and maxAvgDisp > avgDisp):
            tuple = (scorePerWeight, avgDisp, individual)
            sortingList.append(tuple)

    if len(sortingList) is 0:
        print("--ERROR--")
        print("Check that your maxWeight, maxDispOfAnyTargetNode and maxAvgDisp are not set too low")
        errorFlag = True
        break

    sortingList.sort(key = sortingKey, reverse=True)
    seeds.clear()
    for i in range(numSeeds):
        seeds.append(sortingList.__getitem__(i)[2])

    bestInd = sortingList.__getitem__(0)
    bestIndScore = bestInd[0]
    bestIndAvgDisp = bestInd[1]
    bestIndFrame = bestInd[2]
    if maxScorePerWeight < sortingList.__getitem__(0)[0]:
        maxScorePerWeight = bestIndScore
        averageDisp = bestIndAvgDisp
        maxFrame = bestIndFrame

    if gen % graphUpdatePeriod is 0:
        ax1.plot(iterations, maxScoresPerWeight)
        ax2.plot(iterations, averageDisps)
        ax3.plot(iterations, weights)
        ax4.clear()
        maxFrame.plotAni(ax4)
        plt.pause(0.001)

    maxScoresPerWeight.append(maxScorePerWeight)
    averageDisps.append(averageDisp)
    iterations.append(gen)
    weights.append(maxFrame.weight)
    if gen is 1:
        endOneFrame = time.time()
        minutesPerGen = (endOneFrame - startOneFrame) / 60
        numFramesAnalyzed = numGenerations * numSeeds * numChildrenPerSeed
        print("\nYou have elected to analyze", numFramesAnalyzed, "frames")
        print("across",numGenerations,"generations (i.e.",int(numFramesAnalyzed/numGenerations),"per generation)")
        print("\nThis will take an estimated", '%.1f' % (minutesPerGen * numGenerations), "minutes to complete")
    print("\n")
    print("Generation No.", gen)
    print("Max Score Per Weight:\t\t", maxScorePerWeight)
    print("Total Weight:\t\t\t\t", maxFrame.weight)
    print("Avg Disp. of Target Nodes:\t", averageDisp)

ax1.plot(iterations, maxScoresPerWeight)
ax2.plot(iterations, averageDisps)
ax3.plot(iterations, weights)
maxFrame.plotAni(ax4)

if not errorFlag:
    print("\n--FINISHED--")

    print("\n--STATS--")
    end = time.time()
    minutesTaken = (end - start) / 60
    print("\nMinutes taken for simulation to complete:", minutesTaken)
    print("\nTotal Number of Frames Analyzed:", numFramesAnalyzed)
    print("\nThe best frame's score was", '%.3f' % (maxScorePerWeight-baseFrameScorePerWeight))
    print("better than the original seed frame")
    print("\nThe weight of the best frame was")
    print('%.2f' % (baseFrame.weight-maxFrame.weight), "pounds less than the original seed frame")
    print("\nThe avg. displacement of all target nodes for the best frame was")
    print('%.5f' % (baseFrameAvgDisp-averageDisp), "inches less than the original seed frame")

    # Plot graphs and frame/displacements
    plt.show()
    for loadCase in LoadCases.listLoadCases:
        maxFrame.setLoadCase(loadCase)
        maxFrame.solve()
        maxFrame.plot(50)

