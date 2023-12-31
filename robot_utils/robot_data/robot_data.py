import numpy as np

class NoDataNearTimeException(Exception):
    
    def __init__(self, t_desired, t_closest=None):
        message = f"Desired time: {t_desired}. Closest time: {t_closest}"
        super().__init__(message)

class RobotData():
    """
    Parent class for easy access to robotics data over time
    """
    def __init__(self, time_tol=.1, interp=False):
        self.time_tol = time_tol
        self.interp = interp
        
    def set_t0(self, t0):
        self.times += -self.times[0] + t0
        
    def set_times(self, times):
        self.times = times
            
    def idx(self, t):
        """
        Finds the index of pose info closes to the desired time.

        Args:
            t (float): time

        Returns:
            int: Index of pose info closest to desired time or None if no time is available within 
                tolerance.
        """
        op1_exists = np.where(self.times <= t)[0].shape[0]
        op2_exists = np.where(self.times >= t)[0].shape[0]
        if not op1_exists and not op2_exists:
            raise NoDataNearTimeException(t_desired=t)
        if op1_exists:
            op1 = np.where(self.times <= t)[0][-1]
        if op2_exists:
            op2 = np.where(self.times >= t)[0][0]
            
        if not op1_exists: 
            idx = op2 if not self.interp else [op2, op2]
        elif not op2_exists: 
            idx = op1 if not self.interp else [op1, op1]
        elif self.interp:
            idx = [op1, op2]
        elif abs(t - self.times[op1]) < abs(t - self.times[op2]): 
            idx = op1
        else: 
            idx = op2
        
        if self.interp and (abs(self.times[idx[0]] - t) > self.time_tol or \
                            abs(self.times[idx[1]] - t) > self.time_tol):
            raise NoDataNearTimeException(t_desired=t, 
                                          t_closest=[self.times[idx[0]], self.times[idx[1]]])
        elif self.interp:
            return idx
        # check to make sure found time is close enough
        elif abs(self.times[idx] - t) > self.time_tol:
            raise NoDataNearTimeException(t_desired=t, t_closest=self.times[idx])
        else: 
            return idx
        
    def get_val(self, val, t):
        idx = self.idx(t)
        return val[idx]
        
    def __len__(self):
        return len(self.times)
