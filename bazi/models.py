from django.db import models

class FortuneRecord(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="ชื่อ")
    last_name = models.CharField(max_length=100, verbose_name="นามสกุล")
    email = models.EmailField(blank=True, null=True, verbose_name="อีเมล")
    gender = models.CharField(max_length=10, default="male", verbose_name="เพศ")
    
    birth_day = models.IntegerField(default=1, verbose_name="วันเกิด")
    birth_month = models.IntegerField(default=1, verbose_name="เดือนเกิด")
    birth_year = models.IntegerField(default=1995, verbose_name="ปีเกิด")
    birth_hour = models.IntegerField(default=9, verbose_name="ชั่วโมงเกิด")
    birth_minute = models.IntegerField(default=30, verbose_name="นาทีเกิด")
    
    province = models.CharField(max_length=100, default="กรุงเทพมหานคร", verbose_name="จังหวัด")
    country = models.CharField(max_length=100, default="ประเทศไทย", verbose_name="ประเทศ")
    
    chart_data = models.JSONField(blank=True, null=True, verbose_name="ข้อมูลดวงที่วิเคราะห์")
    
    status = models.CharField(max_length=20, default="Active", verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    last_analyzed_at = models.DateTimeField(auto_now=True, verbose_name="วิเคราะห์ล่าสุดเมื่อ")

    class Meta:
        ordering = ['-last_analyzed_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.birth_day}/{self.birth_month}/{self.birth_year})"
