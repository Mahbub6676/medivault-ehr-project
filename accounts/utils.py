"""Small shared helpers used across the MediVault apps."""


def next_code(model, field, prefix, width=5):
    """Return the next human readable identifier, e.g. ``PAT-00001``.

    The function looks at the highest primary key of the table and keeps
    increasing the counter until an unused code is found. Simple, readable and
    robust identifier generation.
    """

    last = model.objects.order_by("-id").first()
    number = (last.pk + 1) if last else 1
    code = f"{prefix}-{number:0{width}d}"
    while model.objects.filter(**{field: code}).exists():
        number += 1
        code = f"{prefix}-{number:0{width}d}"
    return code


def bootstrap_form(form, placeholders=None):
    """Add Bootstrap 5 CSS classes (and placeholders) to every form widget."""
    placeholders = placeholders or {}
    for name, field in form.fields.items():
        widget = field.widget
        css = widget.attrs.get("class", "")
        input_type = getattr(widget, "input_type", "")
        if input_type == "checkbox":
            widget.attrs["class"] = (css + " form-check-input").strip()
        elif widget.__class__.__name__ in ("Select", "SelectMultiple", "NullBooleanSelect"):
            widget.attrs["class"] = (css + " form-select").strip()
        else:
            widget.attrs["class"] = (css + " form-control").strip()
        if name in placeholders:
            widget.attrs["placeholder"] = placeholders[name]
        elif input_type in ("text", "email", "password", "number", "tel"):
            widget.attrs.setdefault("placeholder", field.label or name.replace("_", " ").title())
