def getIterAll(pastDaysRange, maRange):
    iterAll = []
    for pastDays in pastDaysRange:
        for maValue in maRange:
            realPreDf, ratio = lRPredict(df, backtestStartDate, backtestEndDate, forecastDays, pastDays, maValue,
                                         stepMonth, sampleDataSize)
            iterAll.append([pastDays, maValue, ratio])
            print(f'pastDays = {pastDays}, ma = {maValue}, ratio={ratio}', end='\r')
    iterAllDf = pd.DataFrame(iterAll, columns=['pastDays', 'ma', 'ratio'])
    iterAllDf.to_csv(iterAllDfPath, encoding='utf-8-sig', index=False)