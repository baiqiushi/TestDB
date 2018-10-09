import csv
import time
import QualityUtil
import os


# k value percentage of the keyword frequency
# 5 - 100, step = 5
k_percentages = range(5, 100, 5)


# generate curves of p_keywords on p_table in p_db
# p_db: handle of database
# p_table: name of table on which we'll generate curves
# p_keywords: list of keywords, [w1, w2, w3, ...]
# p_scale: [x_scale, y_scale], based on the table sampled ratio
# return a list of curves = [{p_table}, quality_function, w1, q(5%), q(10%), ..., q(95%), query_time, cal_curve_time]
def generateCurves(p_db, p_table, p_keywords, p_scale, p_quality_function='PH'):

    x_scale = p_scale[0]
    y_scale = p_scale[1]

    curves = []

    t = time.time()
    progress = 0
    skipped = 0
    for keyword in p_keywords:
        progress += 1
        curve = [p_table, p_quality_function, keyword]

        # 1. Get total coordinates of this keyword
        t0 = time.time()
        totalCoordinates = p_db.GetCoordinate(p_table, keyword, -1)
        if len(totalCoordinates) == 0:
            skipped += 1
            continue

        # 2. for each k percentage calculate the quality value
        t1 = time.time()
        for k_percentage in k_percentages:
            if p_quality_function == 'PH':
                similarity = QualityUtil.phQualityOfKPercentage(totalCoordinates, k_percentage, x_scale, y_scale)
            else:
                similarity = 0.0
            curve.append(similarity)
        t2 = time.time()

        # The last 2 elements are the query time and curve generation time of this keyword
        curve.append(t1 - t0)  # query time
        curve.append(t2 - t1)  # curve generation time
        curves.append(curve)

        # output time information to console
        print keyword, \
            ", [query]", t1 - t0, \
            ", [curve]", t2 - t1, \
            ", [total]", time.time() - t0, \
            ", [All]", time.time() - t, \
            ", [progress]", str(progress * 100 / len(p_keywords)) + '%'

    return curves


# write the generated curves into a csv file
# p_table: the table from which the curves are generated
# p_curves: the curves generated by the generateCurves function in this file
# p_csvFilePath: absolute file path for the target csv file to write to
# csv file name: {p_table}_curves.csv
# csv file format: [{p_table}, quality_function, keyword, q(5%), q(10%), ..., q(95%), query_time, cal_curve_time]
# return: csv file (absolute path to the file)
def writeCurvesToCSV(p_table, p_curves, p_csvFilePath):
    l_csvFile = p_csvFilePath + '/' + p_table + '_curves.csv'
    with open(l_csvFile, 'a') as csvFile:
        csvWriter = csv.writer(csvFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for curve in p_curves:
            csvWriter.writerow(curve)
    return l_csvFile


# load the curves csv file into database
# p_db: database handle
# p_csvFile: absolute path to the csv file returned by the writeCurvesToCSV function in this file
def loadCurvesCSVToDB(p_db, p_csvFile):
    return p_db.loadCSVToTable(os.path.abspath(p_csvFile), 'word_curves')


# insert the curves into database
# p_db: database handle
# p_curves: the curves generated by the generateCurves function in this file
def insertCurvesToDB(p_db, p_curves):
    for curve in p_curves:
        success = p_db.insertListToTable(curve, 'word_curves')
        if not success:
            print '[x] insert failed.'
    return True
