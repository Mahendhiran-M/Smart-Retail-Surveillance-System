class RiskFusion:
    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def compute_final_risk(self, lstm_prob, conceal_score, dwell_score, exit_score):
        # Apply the fusion formula
        risk_score = (0.4 * lstm_prob) + \
                     (0.2 * conceal_score) + \
                     (0.2 * dwell_score) + \
                     (0.2 * exit_score)
        
        trigger_alert = bool(risk_score > self.threshold)
        
        return risk_score, trigger_alert