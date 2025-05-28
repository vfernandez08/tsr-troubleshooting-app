import os
import json
from openai import OpenAI

class TroubleshootingAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_speed_test_and_alarms(self, speed_test_data, alarm_data, customer_info):
        """
        Analyze speed test results and alarm data to suggest troubleshooting steps
        """
        # Prepare the analysis prompt
        prompt = f"""
You are an expert fiber internet technical support specialist. Based on the following customer data, provide specific troubleshooting recommendations.

CUSTOMER SPEED TEST DATA:
- Device Used: {speed_test_data.get('device_type', 'N/A')}
- GHz Band: {speed_test_data.get('ghz_band', 'N/A')}
- Download Speed: {speed_test_data.get('download_speed', 'N/A')} Mbps
- Upload Speed: {speed_test_data.get('upload_speed', 'N/A')} Mbps
- Speed Test App: {speed_test_data.get('test_app', 'N/A')}
- Expected Package Speed: {customer_info.get('speed_package', 'N/A')}

ALARM/STREAM DATA:
{alarm_data.get('alarm_details', 'No alarms detected')}

ONT EQUIPMENT:
- ONT Type: {customer_info.get('ont_type', 'Nokia')}
- Router Type: {customer_info.get('router_type', 'Eero')}

Please provide 3-5 specific troubleshooting steps in order of priority. Focus on:
1. Speed optimization based on device band and speeds
2. Addressing any alarms found
3. Equipment-specific recommendations for Nokia ONT + Eero setup
4. Connection and configuration checks

Format your response as a numbered list with brief explanations for each step.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using the cost-effective model you mentioned
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fiber internet technical support expert. Provide clear, actionable troubleshooting steps based on speed test and alarm data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent technical advice
            )
            
            return {
                "success": True,
                "recommendations": response.choices[0].message.content,
                "model_used": "gpt-4o-mini"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_recommendations": self._get_fallback_recommendations(speed_test_data, alarm_data)
            }
    
    def _get_fallback_recommendations(self, speed_test_data, alarm_data):
        """
        Provide basic recommendations if AI fails
        """
        recommendations = []
        
        # Speed-based recommendations
        download_speed = speed_test_data.get('download_speed', 0)
        if isinstance(download_speed, str):
            try:
                download_speed = float(download_speed)
            except:
                download_speed = 0
                
        if download_speed < 100:
            recommendations.append("1. Check device connection - consider switching to 5GHz band for better speeds")
            recommendations.append("2. Reboot ONT and router to refresh connection")
            
        # Band-specific recommendations  
        ghz_band = speed_test_data.get('ghz_band', '').lower()
        if '2.4' in ghz_band:
            recommendations.append("3. Move device to 5GHz network for improved performance")
            
        # Alarm-based recommendations
        if 'alarm' in alarm_data.get('alarm_details', '').lower():
            recommendations.append("4. Address active alarms - check ONT light status and connections")
            
        recommendations.append("5. Verify all cable connections are secure")
        
        return "\n".join(recommendations)