A Sublime Text plugins to preview Latex Equation in comment line or block.
The equation image is downloaded from [Online Equation editor](https://www.sublimetext.com/docs/3/minihtml.html).

### Usage

- Hover the cursor over the equation to preview the equation.
- press `ctrl+shift+l` to preview the equation under the cursor.

This works for inline equation and block equation

```python
# $a^2+b^2=c^2$
def test():
    print("hello world!")

# $$
# \begin{align*}
#   a_{11}x_1 + a_{12}x_2 = c1 \\
#   a_{21}x_1 + a_{22}x_2 = c2
# \end{align*}
# $$
def test2():
    print("hello world!")
```

### To DO

- The display quality of the equation image is poor.
  Not use `show_popup` properly?
- Use local LaTex engine to convert LaTex equations.
- Cache images. 
- Sometimes `FileNotFoundError` occurs when delete images.