-- إصلاح التريغر القديم handle_scheduled_order
DROP TRIGGER IF EXISTS trg_handle_scheduled_order ON orders;

-- إنشاء تريغر جديد يسمح بـ pending للطلبات الجديدة
CREATE OR REPLACE FUNCTION handle_scheduled_order()
RETURNS TRIGGER AS $$
DECLARE
  v_prep_minutes INTEGER := 0;
  v_prep_interval INTERVAL := INTERVAL '0';
  v_expected_delivery INTERVAL := INTERVAL '0';
  v_total_required INTERVAL := INTERVAL '0';
  v_now TIMESTAMP := NOW();
  v_new_status order_status_enum := NEW.status;
  v_new_is_scheduled BOOLEAN := COALESCE(NEW.is_scheduled, FALSE);
BEGIN
  -- إذا كان الطلب جديد (INSERT) ونوعه pending، نتركه كما هو
  IF TG_OP = 'INSERT' AND NEW.status = 'pending' THEN
    RETURN NEW;
  END IF;

  -- زمن التحضير من المطعم
  IF NEW.restaurant_id IS NOT NULL THEN
    SELECT estimated_preparation_time
      INTO v_prep_minutes
    FROM restaurants
    WHERE restaurant_id = NEW.restaurant_id;

    v_prep_interval := make_interval(mins => COALESCE(v_prep_minutes, 0));
  END IF;

  -- زمن التوصيل المتوقع من order_timings (إن وجد)
  IF NEW.order_id IS NOT NULL THEN
    SELECT expected_delivery_duration
      INTO v_expected_delivery
    FROM order_timings
    WHERE order_id = NEW.order_id
    LIMIT 1;

    IF NOT FOUND THEN
      v_expected_delivery := INTERVAL '0';
    END IF;
  END IF;

  v_total_required := v_prep_interval + v_expected_delivery + INTERVAL '5 minutes';

  -- منطق الجدولة
  IF NEW.delivery_method = 'pick_up' THEN
    -- الاستلام الذاتي لا يحتاج كابتن
    IF NEW.scheduled_time IS NOT NULL THEN
      IF NEW.scheduled_time - v_now > (v_prep_interval + INTERVAL '5 minutes') THEN
        v_new_status := 'waiting_restaurant_acceptance';
        v_new_is_scheduled := TRUE;
      ELSE
        v_new_status := 'processing';
        v_new_is_scheduled := FALSE;
      END IF;
    ELSE
      -- بدون موعد محدد - نترك الحالة كما هي
      v_new_status := NEW.status;
      v_new_is_scheduled := FALSE;
    END IF;

  ELSE
    -- توصيل عادي
    IF NEW.scheduled_time IS NOT NULL THEN
      IF NEW.scheduled_time - v_now > v_total_required THEN
        v_new_status := 'waiting_restaurant_acceptance';
        v_new_is_scheduled := TRUE;
      ELSE
        v_new_status := 'processing';
        v_new_is_scheduled := FALSE;
      END IF;
    ELSE
      -- غير مجدول - نترك الحالة كما هي
      v_new_status := NEW.status;
      v_new_is_scheduled := FALSE;
    END IF;
  END IF;

  -- تعيين القيم مباشرة لأن التريغر BEFORE
  NEW.status := v_new_status;
  NEW.is_scheduled := v_new_is_scheduled;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_handle_scheduled_order
BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW
EXECUTE FUNCTION handle_scheduled_order();
