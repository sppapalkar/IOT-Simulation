import matplotlib
import matplotlib.pyplot as plt

class Result:
    def __init__(self):
        self.nrt_miat = []
        self.rt_mean = []
        self.rt_percentile = []
        self.nrt_mean = []
        self.nrt_percentile = []
        self.rtci = []
        self.nrtci = []
        self.percentile_rtci = []
        self.percentile_nrtci = []

    def display(self):
        print("\n-----------------------------------Final Results-----------------------------------")
        print("NRT MIAT: ",self.nrt_miat)
        print("RT Mean: ",self.rt_mean)
        print("RT Mean CI: ",self.rtci)
        print("RT 95 Percentile: ",self.rt_percentile)
        print("RT 95 Percentile CI: ",self.percentile_rtci)
       
        print("\nnRT Mean: ",self.nrt_mean)
        print("nRT Mean CI: ",self.nrtci)
        print("nRT 95 Percentile: ",self.nrt_percentile)
        print("nRT 95 Percentile CI: ",self.percentile_nrtci)
        
        self.plot_graph()

    def plot_graph(self):
        fig = plt.figure()
        w = 0.8
        
        ax1 = fig.add_subplot(1,1,1)
        x1 = [(n-w/2) for n in self.nrt_miat]
        ci1 = [((x[1]-x[0])/2) for x in self.rtci]
        
        x2 = [(n+w/2) for n in self.nrt_miat]
        ci2 = [((x[1]-x[0])/2) for x in self.nrtci]

        bar1 = ax1.bar(x1, self.rt_mean, color='b', yerr=ci1, capsize = 3, width = w, label='RT message')
        bar2 = ax1.bar(x2, self.nrt_mean, color='g', yerr=ci2, capsize = 3, width = w, label='non-RT message')
        
        ax1.set_xlabel('Mean inter-arrival time of non-RT message')
        ax1.set_ylabel('Mean Response Time')
        ax1.legend((bar1[0], bar2[0]), ('RT messages', 'Non-RT messages'))
        ax1.set_title("Means Plot")
        
        plt.show()
        
        fig = plt.figure()
        ax2 = fig.add_subplot(1,1,1)
        
        ci1_2 = [((x[1]-x[0])/2) for x in self.percentile_rtci]
        ci2_2 = [((x[1]-x[0])/2) for x in self.percentile_nrtci]

        bar3 = ax2.bar(x1, self.rt_percentile, color='b', yerr=ci1_2, capsize = 3, width = w, label='RT message')
        bar4 = ax2.bar(x2, self.nrt_percentile, color='g', yerr=ci2_2, capsize = 3, width = w, label='non-RT message')
        
        ax2.set_xlabel('Mean inter-arrival time of non-RT message')
        ax2.set_ylabel('Mean 95th percentile response time')
        ax2.legend((bar1[0], bar2[0]), ('RT messages', 'Non-RT messages'))
        ax2.set_title("Percentile Plot")
        plt.show()